import os
import torch
import logging
from dotenv import load_dotenv, find_dotenv

# Import packages from src

import src.ai.model_gpu as model_gpu

# We re-export the packages
__all__ = [
    'model_gpu',
]

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

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
THREADS_MAX_WORKERS = get_env_variable('THREADS_MAX_WORKERS', int, 10)

# Model Settings

MODEL_ID = get_env_variable('MODEL_ID', str, "meta-llama/Meta-Llama-3-8B-Instruct")
CONVERT_TOKENS_TO_IDS = get_env_variable('CONVERT_TOKENS_TO_IDS', str, "<|eot_id|>")

# Torch DType
# We can expand support here for other types
if os.getenv('TORCH_DTYPE') == "bfloat16":
    TORCH_DTYPE = torch.bfloat16
# Default value
else:
    TORCH_DTYPE = torch.bfloat16

# Set the environment variable for MPS fallback
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

# What device are we using
logger.info(f"Using device: {model_gpu.device}")

# Model Inference Settings

DEFAULT_DO_SAMPLE = get_env_variable('DEFAULT_DO_SAMPLE', str_to_bool, True)
DEFAULT_MAX_NEW_TOKENS = get_env_variable('DEFAULT_MAX_NEW_TOKENS', int, 256)
DEFAULT_TEMPERATURE = get_env_variable('DEFAULT_TEMPERATURE', float, 0.6)
DEFAULT_TOP_P = get_env_variable('DEFAULT_TOP_P', float, 0.7)

# CORS

DEFAULT_ACCESS_CONTROL_MAX_AGE = get_env_variable('DEFAULT_ACCESS_CONTROL_MAX_AGE', str, "86400")
DEFAULT_ACCESS_CONTROL_ALLOW_ORIGIN = get_env_variable('DEFAULT_ACCESS_CONTROL_ALLOW_ORIGIN', str, "*")