import os
from openai import OpenAI
from src.commons.utils import get_server_logger
from src.core.guardrails import get_guardrail_handler
from src.core.function_calling import (
    CurveIntentConfig,
    CurveIntentHandler,
    CurveFunctionConfig,
    CurveFunctionHandler,
)


# Define logger
logger = get_server_logger()


# Define the client
CURVE_ENDPOINT = os.getenv("CURVE_ENDPOINT", "https://api.fc.curve.com/v1")
CURVE_API_KEY = "EMPTY"
CURVE_CLIENT = OpenAI(base_url=CURVE_ENDPOINT, api_key=CURVE_API_KEY)

# Define model names
CURVE_INTENT_MODEL_ALIAS = "Curve-Intent"
CURVE_FUNCTION_MODEL_ALIAS = "Curve-Function"
CURVE_GUARD_MODEL_ALIAS = "curvelaboratory/Curve-Guard"

# Define model handlers
handler_map = {
    "Curve-Intent": CurveIntentHandler(
        CURVE_CLIENT, CURVE_INTENT_MODEL_ALIAS, CurveIntentConfig
    ),
    "Curve-Function": CurveFunctionHandler(
        CURVE_CLIENT, CURVE_FUNCTION_MODEL_ALIAS, CurveFunctionConfig
    ),
    "Curve-Guard": get_guardrail_handler(CURVE_GUARD_MODEL_ALIAS),
}
