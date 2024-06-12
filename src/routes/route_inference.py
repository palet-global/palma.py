import asyncio
import src.restapi.constants as constants
import src.utils.validators as validators
from src.restapi.json import read_json_request
from starlette.responses import Response
from starlette.responses import StreamingResponse
import src.ai.model_inference as model_inference
import src.ai.model_streaming as model_streaming

# route_inference
async def inference(request, tokenizer, model, terminators, shared_executor):
    # Lets read the json request
    (json_data, json_error, status_code) = await read_json_request(request)
    
    # Lets check for errors on the json request
    if not validators.is_empty(json_error):
        return Response(content=json_error, media_type=constants.HTTP_DEFAULT_CONTENT_TYPE, status_code=status_code)

    # Create an asyncio Queue to hold the response
    response_queue = asyncio.Queue()

    # stream validation
    # default value of false
    stream = json_data.get("stream", False)
    if not validators.is_bool(stream):
        stream = False

    # if we are doing normal inference
    if not stream:
        # Schedule the start_generating function to run as a background task
        asyncio.create_task(
            model_inference.start_generating(
                response_queue, 
                json_data, 
                tokenizer, 
                model, 
                terminators, 
                shared_executor
            )
        )

        # Return the output as a JSON response
        json_data = await model_inference.catch_token(response_queue)
        return Response(content=json_data, media_type=constants.HTTP_DEFAULT_CONTENT_TYPE, status_code=200)

    # if we are streaming
    else:
        # Schedule the start_streaming function to run as a background task
        asyncio.create_task(
            model_streaming.start_streaming(
                response_queue, 
                json_data, 
                tokenizer, 
                model, 
                terminators, 
                shared_executor
            )
        )

        # Return a streaming response with SSE media type
        return StreamingResponse(model_streaming.catch_token(response_queue), media_type='text/event-stream', status_code=200)