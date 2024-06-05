import asyncio
import src.restapi.constants as constants
import src.utils.validators as validators
from src.restapi.json import read_json_request
from starlette.responses import Response
import src.ai.model_inference as model_inference

# route_inference
async def inference(request, tokenizer, model, terminators, shared_executor):
    # Lets read the json request
    (json_data, json_error, status_code) = await read_json_request(request)
    
    # Lets check for errors on the json request
    if not validators.is_empty(json_error):
        return Response(content=json_error, media_type=constants.HTTP_DEFAULT_CONTENT_TYPE, status_code=status_code)

    # Create an asyncio Queue to hold the response
    response_queue = asyncio.Queue()

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
    json = await model_inference.catch_token(response_queue)
    return Response(content=json, media_type=constants.HTTP_DEFAULT_CONTENT_TYPE, status_code=200)