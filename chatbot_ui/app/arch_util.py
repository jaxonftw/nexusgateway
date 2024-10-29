import json


CURVE_STATE_HEADER = "x-curve -state"


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
