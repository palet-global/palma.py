import src.utils.validators as validators
from config import (
    DEFAULT_DO_SAMPLE,
    DEFAULT_MAX_NEW_TOKENS,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P
)

# Function for sanitazing the inference parameters
def get_safe_parameters(json_data):
    # Access messages value, it should never be empty
    # Due to prior JSON request verifications
    messages = json_data.get("messages", "")

    # If empty we establish default values
    max_new_tokens = json_data.get("max_new_tokens", DEFAULT_MAX_NEW_TOKENS)
    do_sample = json_data.get("do_sample", DEFAULT_DO_SAMPLE)
    temperature = json_data.get("temperature", DEFAULT_TEMPERATURE)
    top_p = json_data.get("top_p", DEFAULT_TOP_P)

    # Lets sanitate values
    if not validators.is_numeric(max_new_tokens):
        max_new_tokens = DEFAULT_MAX_NEW_TOKENS
    if not validators.is_bool(do_sample):
        do_sample = DEFAULT_DO_SAMPLE
    if not validators.is_numeric(temperature):
        temperature = DEFAULT_TEMPERATURE
    if not validators.is_numeric(top_p):
        top_p = DEFAULT_TOP_P

    # Lets return the values
    return (messages, max_new_tokens, do_sample, temperature, top_p)