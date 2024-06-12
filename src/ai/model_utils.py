import src.utils.validators as validators
from config import (
    DEFAULT_DO_SAMPLE,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P
)

# Function for sanitazing the inference parameters
def get_safe_parameters(json_data):
    # Access messages value, it should never be empty
    # Due to prior JSON request verifications
    messages = json_data.get("messages", "")

    # If empty we establish default values
    max_tokens = json_data.get("max_tokens", DEFAULT_MAX_TOKENS)
    temperature = json_data.get("temperature", DEFAULT_TEMPERATURE)
    top_p = json_data.get("top_p", DEFAULT_TOP_P)

    # Open AI API do not support do_sample
    # So we default to the .env configuration
    do_sample = DEFAULT_DO_SAMPLE

    # Lets sanitate values
    if not validators.is_numeric(max_tokens):
        max_tokens = DEFAULT_MAX_TOKENS
    if not validators.is_numeric(temperature):
        temperature = DEFAULT_TEMPERATURE
    if not validators.is_numeric(top_p):
        top_p = DEFAULT_TOP_P

    # Lets return the values
    return (messages, max_tokens, do_sample, temperature, top_p)