import json
import asyncio
from typing import Optional
import src.ai.model_utils as model_utils
from transformers import AutoTokenizer, TextStreamer
from config import (
    model_gpu
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
        
# Run the streaming_wrapper coroutine in the executor
async def start_streaming(response_queue, json_data, tokenizer, model, terminators, shared_executor):
    loop = asyncio.get_event_loop()
    streamer = AsyncTextIteratorStreamer(tokenizer, response_queue, True)
    await loop.run_in_executor(
            shared_executor, 
            lambda: asyncio.run(
                streaming_wrapper(streamer, json_data, tokenizer, model, terminators)
            )
        )
        
# Define an asynchronous wrapper function for model streaming
async def streaming_wrapper(streamer, json_data, tokenizer, model, terminators):
    streaming(streamer, json_data, tokenizer, model, terminators)
    
    # Signal the end of streaming by calling the end method on the streamer
    streamer.end()
        
# Function for streaming inference
def streaming(streamer, json_data, tokenizer, model, terminators):

    # Lets sanitize the parameters
    (messages, max_new_tokens, do_sample, temperature, top_p) = model_utils.get_safe_parameters(json_data)

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

# Catch the token that are being streamed
async def catch_token(response_queue):
    while True:
        # Catch the token that are being generated
        outputs = await response_queue.get()

        # If no more tokens, lets end streaming
        if outputs is None:
            break

        # Stream data
        yield f"data: {json.dumps(outputs)}\n\n"