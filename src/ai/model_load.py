from concurrent.futures import ThreadPoolExecutor
from transformers import AutoTokenizer, AutoModelForCausalLM

from config import (
    model_gpu, 
    THREADS_MAX_WORKERS,
    MODEL_ID,
    CONVERT_TOKENS_TO_IDS,
    TORCH_DTYPE
)

def init():
    try:
        # Load the tokens
        tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)

        # Load the model
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            torch_dtype=TORCH_DTYPE,
            device_map=model_gpu.device,
        )

        # Lets set the terminators
        terminators = [
            tokenizer.eos_token_id,
            tokenizer.convert_tokens_to_ids(CONVERT_TOKENS_TO_IDS)
        ]

        # Shared Thread Pool Executor
        shared_executor = ThreadPoolExecutor(max_workers=THREADS_MAX_WORKERS)

        return {
            "tokenizer": tokenizer, 
            "model": model, 
            "terminators": terminators, 
            "shared_executor": shared_executor
        }
    except Exception as e:
        # Handle initialization error
        print(f"Error initializing model dependencies: {e}")
        raise
