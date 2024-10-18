import json
import os
from openai import OpenAI, DefaultHttpxClient
import gradio as gr
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

log = logging.getLogger(__name__)

CHAT_COMPLETION_ENDPOINT = os.getenv("CHAT_COMPLETION_ENDPOINT")
CURVE_STATE_HEADER = "x-curve -state"
log.info(f"CHAT_COMPLETION_ENDPOINT: {CHAT_COMPLETION_ENDPOINT}")

client = OpenAI(
    api_key="--",
    base_url=CHAT_COMPLETION_ENDPOINT,
    http_client=DefaultHttpxClient(headers={"accept-encoding": "*"}),
)


def predict(message, state):
    if "history" not in state:
        state["history"] = []
    history = state.get("history")
    history.append({"role": "user", "content": message})
    log.info(f"history: {history}")

    # Custom headers
    custom_headers = {
        "x-curve -deterministic-provider": "openai",
    }

    try:
        raw_response = client.chat.completions.with_raw_response.create(
            model="--",
            messages=history,
            temperature=1.0,
            # metadata=metadata,
            extra_headers=custom_headers,
        )
    except Exception as e:
        log.info(e)
        # remove last user message in case of exception
        history.pop()
        log.info("Error calling gateway API: {}".format(e.message))
        raise gr.Error("Error calling gateway API: {}".format(e.message))

    log.error(f"raw_response: {raw_response.text}")
    response = raw_response.parse()

    # extract curve _state from metadata and store it in gradio session state
    # this state must be passed back to the gateway in the next request
    response_json = json.loads(raw_response.text)
    if response_json:
        # load curve _state from metadata
        curve _state_str = response_json.get("metadata", {}).get(CURVE_STATE_HEADER, "{}")
        # parse curve _state into json object
        curve _state = json.loads(curve _state_str)
        # load messages from curve _state
        curve _messages_str = curve _state.get("messages", "[]")
        # parse messages into json object
        curve _messages = json.loads(curve _messages_str)
        # append messages from curve  gateway to history
        for message in curve _messages:
            history.append(message)

    content = response.choices[0].message.content

    history.append({"role": "assistant", "content": content, "model": response.model})

    # for gradio UI we don't want to show raw tool calls and messages from developer application
    # so we're filtering those out
    history_view = [h for h in history if h["role"] != "tool" and "content" in h]
    messages = [
        (history_view[i]["content"], history_view[i + 1]["content"])
        for i in range(0, len(history_view) - 1, 2)
    ]
    return messages, state


with gr.Blocks(fill_height=True, css="footer {visibility: hidden}") as demo:
    print("Starting Demo...")
    chatbot = gr.Chatbot(label="Curve Chatbot", scale=1)
    state = gr.State({})
    with gr.Row():
        txt = gr.Textbox(
            show_label=False,
            placeholder="Enter text and press enter",
            scale=1,
            autofocus=True,
        )

    txt.submit(predict, [txt, state], [chatbot, state])

demo.launch(server_name="0.0.0.0", server_port=8080, show_error=True, debug=True)
