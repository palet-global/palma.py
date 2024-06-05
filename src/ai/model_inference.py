import json
import asyncio
import src.ai.model_utils as model_utils
from config import (
    model_gpu
)

# Run the generate_wrapper coroutine in the executor
async def start_generating(response_queue, json_data, tokenizer, model, terminators, shared_executor):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(shared_executor, lambda: asyncio.run(generate_wrapper(response_queue, json_data, tokenizer, model, terminators)))

# Define an asynchronous wrapper function for model inference
async def generate_wrapper(response_queue, json_data, tokenizer, model, terminators):
    await generate(response_queue, json_data, tokenizer, model, terminators)

# Function to generate inference
async def generate(response_queue, json_data, tokenizer, model, terminators):

    # Lets sanitize the parameters
    (messages, max_new_tokens, do_sample, temperature, top_p) = model_utils.get_safe_parameters(json_data)

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

# Catch the generated tokens
async def catch_token(response_queue):
    # Catch the token that are being generated
    outputs = await response_queue.get()

    # Json response
    json_response = {
        "data": outputs,
    }

    # Do NOT use pretty-print here as its 3x slower than normal dump
    # And we want to return this response to the user as FAST as possible
    json_response = json.dumps(json_response)

    return json_response