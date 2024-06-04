# Env

import os
import torch
from dotenv import load_dotenv, find_dotenv

# Import packages from src

import src.ai.model_gpu as model_gpu

# We re-export the packages
__all__ = [
    'model_gpu',
]

# Check if the .env file exists and load it
dotenv_path = find_dotenv()
if not dotenv_path:
    raise FileNotFoundError("The .env file is missing. Please create one in the root directory.")

load_dotenv(dotenv_path)

def str_to_bool(value):
    return value.lower() in {'true', '1', 't', 'y', 'yes'}
def get_env_variable(name, cast_type=str, default=None):
    value = os.getenv(name, default)
    try:
        return cast_type(value)
    except (TypeError, ValueError):
        raise ValueError(f"Environment variable {name} is not of type {cast_type.__name__}")

# General Configuration

DEBUG = get_env_variable('DEBUG', str_to_bool, False)
THREADS_MAX_WORKERS = get_env_variable('THREADS_MAX_WORKERS', int)

# Model Settings

MODEL_ID = get_env_variable('MODEL_ID')

CONVERT_TOKENS_TO_IDS = get_env_variable('CONVERT_TOKENS_TO_IDS')

# Torch DType
# We can expand support here for other types
if os.getenv('TORCH_DTYPE') == "bfloat16":
    TORCH_DTYPE = torch.bfloat16
# Default value
else:
    TORCH_DTYPE = torch.bfloat16

# Model Inference Settings

DEFAULT_DO_SAMPLE = get_env_variable('DEFAULT_DO_SAMPLE', str_to_bool)
DEFAULT_MAX_NEW_TOKENS = get_env_variable('DEFAULT_MAX_NEW_TOKENS', int)
DEFAULT_TEMPERATURE = get_env_variable('DEFAULT_TEMPERATURE', float)
DEFAULT_TOP_P = get_env_variable('DEFAULT_TOP_P', float)

# CORS

DEFAULT_ACCESS_CONTROL_MAX_AGE = get_env_variable('DEFAULT_ACCESS_CONTROL_MAX_AGE', str, "86400")
DEFAULT_ACCESS_CONTROL_ALLOW_ORIGIN = get_env_variable('DEFAULT_ACCESS_CONTROL_ALLOW_ORIGIN', str, "*")