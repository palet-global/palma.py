import json
import asyncio
import src.restapi.constants as constants
import src.utils.validators as validators
from src.restapi.json import read_json_request
from starlette.responses import Response
import src.ai.model_inference as model_inference
from starlette.responses import StreamingResponse

async def stream(request, tokenizer, model, terminators, shared_executor):
    # Lets read the json request
    (json_data, json_error, status_code) = await read_json_request(request)
    
    # Lets check for errors on the json request
    if not validators.is_empty(json_error):
        return Response(content=json_error, media_type=constants.HTTP_DEFAULT_CONTENT_TYPE, status_code=status_code)

    # Create an asyncio Queue to hold the response
    response_queue = asyncio.Queue()

    ###################################
    ######### START INFERENCE #########

    async def start_streaming():
        # Initialize the streamer with the tokenizer and the response queue, allowing it to stream outputs asynchronously
        streamer = model_inference.AsyncTextIteratorStreamer(tokenizer, response_queue, True)

        # Run the model inference streaming in a separate thread of the shared pool
        await asyncio.get_event_loop().run_in_executor(
            shared_executor, 
            model_inference.streaming, 
            json_data, 
            tokenizer, 
            model, 
            terminators, 
            streamer
        )

        # Signal the end of streaming by calling the end method on the streamer
        streamer.end()

    # Schedule the start_streaming function to run as a background task
    asyncio.create_task(start_streaming())

    ########## END INFERENCE ##########
    ###################################

    # Catch the token that are being streamed
    async def catch_token():
        while True:
            # Retrieve the output from the response queue
            outputs = await response_queue.get()

            # If no more tokens, lets end streaming
            if outputs is None:
                break

            # Stream data
            yield f"data: {json.dumps(outputs)}\n\n"

    # Return a streaming response with SSE media type
    return StreamingResponse(catch_token(), media_type='text/event-stream', status_code=200)