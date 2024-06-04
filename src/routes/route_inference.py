import json
import asyncio
import src.restapi.constants as constants
import src.utils.validators as validators
from src.restapi.json import read_json_request
from starlette.responses import Response
import src.ai.model_inference as model_inference

async def inference(request, tokenizer, model, terminators, shared_executor):
    # Lets read the json request
    (json_data, json_error, status_code) = await read_json_request(request)
    
    # Lets check for errors on the json request
    if not validators.is_empty(json_error):
        return Response(content=json_error, media_type=constants.HTTP_DEFAULT_CONTENT_TYPE, status_code=status_code)

    # Create an asyncio Queue to hold the response
    response_queue = asyncio.Queue()

    ###################################
    ######### START INFERENCE #########

    # Define an asynchronous wrapper function for model inference
    async def async_wrapper():
        await model_inference.generate(response_queue, json_data, tokenizer, model, terminators)

    # Run the async_wrapper coroutine in the executor
    # We use asyncio.run to execute the async_wrapper in a blocking way because run_in_executor 
    # is designed to handle blocking functions. This ensures the asynchronous generate function
    # runs correctly in a separate thread managed by the executor.
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(shared_executor, lambda: asyncio.run(async_wrapper()))

    ########## END INFERENCE ##########
    ###################################

    # Catch the token that are being generated
    outputs = await response_queue.get()

    # Json response
    json_response = {
        "data": outputs,
    }

    # Do NOT use pretty-print as its 3x slower than normal dump
    # And we want to return this message to the user as FAST as possible
    json_response = json.dumps(json_response)

    # Return the output as a JSON response
    return Response(content=json_response, media_type=constants.HTTP_DEFAULT_CONTENT_TYPE, status_code=200)