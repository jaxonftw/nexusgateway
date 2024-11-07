import json
import os


PROMPT_GATEWAY_ENDPOINT = os.getenv(
    "PROMPT_GATEWAY_ENDPOINT", "http://localhost:10000/v1/chat/completions"
)
LLM_GATEWAY_ENDPOINT = os.getenv(
    "LLM_GATEWAY_ENDPOINT", "http://localhost:12000/v1/chat/completions"
)
CURVE_STATE_HEADER = "x-curve -state"

PREFILL_LIST = [
    "May",
    "Could",
    "Sure",
    "Definitely",
    "Certainly",
    "Of course",
    "Can",
]


def get_data_chunks(stream, n=1):
    chunks = []
    for chunk in stream.iter_lines():
        if chunk:
            chunk = chunk.decode("utf-8")
            chunk_data_id = chunk[0:6]
            assert chunk_data_id == "data: "
            chunk_data = chunk[6:]
            chunk_data = chunk_data.strip()
            chunks.append(chunk_data)
            if len(chunks) >= n:
                break
    return chunks


def get_curve _messages(response_json):
    curve _messages = []
    if response_json and "metadata" in response_json:
        # load curve _state from metadata
        curve _state_str = response_json.get("metadata", {}).get(CURVE_STATE_HEADER, "{}")
        # parse curve _state into json object
        curve _state = json.loads(curve _state_str)
        # load messages from curve _state
        curve _messages_str = curve _state.get("messages", "[]")
        # parse messages into json object
        curve _messages = json.loads(curve _messages_str)
        # append messages from curve  gateway to history
        return curve _messages
    return []
