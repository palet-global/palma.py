import asyncio
import src.utils.validators as validators
from typing import Optional
from transformers import AutoTokenizer, TextStreamer
from config import (
    model_gpu, 
    DEFAULT_DO_SAMPLE,
    DEFAULT_MAX_NEW_TOKENS,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P
)

class AsyncTextIteratorStreamer(TextStreamer):
    """
    Streamer that stores print-ready text in an asyncio queue, to be used by a downstream application as an iterator.
    This is useful for applications that benefit from accessing the generated text in a non-blocking way.
    """
    # skip_prompt True its used, to only return the data generated and not the full prompt
    def __init__(
        self, tokenizer: "AutoTokenizer", queue, skip_prompt: bool = False, timeout: Optional[float] = None, **decode_kwargs
    ):
        super().__init__(tokenizer, skip_prompt, **decode_kwargs)
        self.async_queue = queue
        self.stop_signal = None
        self.timeout = timeout
        self.loop = asyncio.get_event_loop()

    def on_finalized_text(self, text: str, stream_end: bool = False):
        """Put the new text in the asyncio queue. If the stream is ending, also put a stop signal in the queue."""
        self.loop.call_soon_threadsafe(self.async_queue.put_nowait, text)
        if stream_end:
            self.loop.call_soon_threadsafe(self.async_queue.put_nowait, self.stop_signal)

    def __iter__(self):
        return self

    def __next__(self):
        value = self.async_queue.get(timeout=self.timeout)
        if value == self.stop_signal:
            raise StopIteration()
        else:
            return value
        
# Function for sanitazing the inference parameters
def get_safe_parameters(json_data):
    # Access messages value, it should never be empty
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

# Function to generate inference
async def generate(response_queue, json_data, tokenizer, model, terminators):

    # Lets sanitize the parameters
    (messages, max_new_tokens, do_sample, temperature, top_p) = get_safe_parameters(json_data)

    # Lets proccess the messages data
    input_ids = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt"
    ).to(model_gpu.device)

    # Manually set the pad_token_id if it's None
    # Assuming EOS token can be used as padding
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id  

    # Attention mask
    attention_mask = (input_ids != tokenizer.pad_token_id).long()
        
    # Perform inference
    outputs = model.generate(
        input_ids,
        attention_mask=attention_mask,
        max_new_tokens=max_new_tokens,
        eos_token_id=terminators,
        pad_token_id=tokenizer.pad_token_id,
        do_sample=do_sample,
        temperature=temperature,
        top_p=top_p,
    )

    # Lets proccess the tokens
    token = outputs[0][input_ids.shape[-1]:]
    response = tokenizer.decode(token, skip_special_tokens=True)

    # Put the processed output into the response queue asynchronously
    await response_queue.put(response)

# Function for streaming inference
def streaming(json_data, tokenizer, model, terminators, streamer):

    # Lets sanitize the parameters
    (messages, max_new_tokens, do_sample, temperature, top_p) = get_safe_parameters(json_data)

    # Lets proccess the messages template
    input_ids = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt"
    ).to(model_gpu.device)

    # Manually set the pad_token_id if it's None
    # Assuming EOS token can be used as padding
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id  

    # Attention mask
    attention_mask = (input_ids != tokenizer.pad_token_id).long()

    # Perform streaming inference
    model.generate(
        input_ids,
        attention_mask=attention_mask,
        streamer=streamer,
        max_new_tokens=max_new_tokens,
        eos_token_id=terminators,
        pad_token_id=tokenizer.pad_token_id,
        do_sample=do_sample,
        temperature=temperature,
        top_p=top_p,
    )