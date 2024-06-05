import asyncio
import src.restapi.constants as constants
import src.utils.validators as validators
from src.restapi.json import read_json_request
from starlette.responses import Response
import src.ai.model_streaming as model_streaming
from starlette.responses import StreamingResponse

# route_stream
async def stream(request, tokenizer, model, terminators, shared_executor):
    # Lets read the json request
    (json_data, json_error, status_code) = await read_json_request(request)
    
    # Lets check for errors on the json request
    if not validators.is_empty(json_error):
        return Response(content=json_error, media_type=constants.HTTP_DEFAULT_CONTENT_TYPE, status_code=status_code)

    # Create an asyncio Queue to hold the response
    response_queue = asyncio.Queue()

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