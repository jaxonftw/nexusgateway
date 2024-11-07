import app.commons.globals as glb
import app.commons.utilities as utils
import app.loader as loader

from app.function_calling.model_handler import CurveFunctionHandler
from app.prompt_guard.model_handler import CurveGuardHanlder

logger = utils.get_server_logger()

curve _function_hanlder = CurveFunctionHandler()
PREFILL_LIST = ["May", "Could", "Sure", "Definitely", "Certainly", "Of course", "Can"]
PREFILL_ENABLED = True
TOOL_CALL_TOKEN = "<tool_call>"
curve _function_endpoint = "https://api.fc.curve.com/v1"
curve _function_client = utils.get_client(curve _function_endpoint)
curve _function_generation_params = {
    "temperature": 0.2,
    "top_p": 1.0,
    "top_k": 50,
    "max_tokens": 512,
    "stop_token_ids": [151645],
}

curve _guard_model_type = {
    "cpu": "curvelaboratory/Curve-Guard-cpu",
    "cuda": "curvelaboratory/Curve-Guard",
    "mps": "curvelaboratory/Curve-Guard",
}

# Model definition
embedding_model = loader.get_embedding_model()
zero_shot_model = loader.get_zero_shot_model()

prompt_guard_dict = loader.get_prompt_guard(curve _guard_model_type[glb.DEVICE])

curve _guard_handler = CurveGuardHanlder(model_dict=prompt_guard_dict)
