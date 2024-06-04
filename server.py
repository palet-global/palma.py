from version import palmapy_version

from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.applications import Starlette
from concurrent.futures import ThreadPoolExecutor
from starlette.middleware.gzip import GZipMiddleware

from transformers import AutoTokenizer, AutoModelForCausalLM

import src.restapi.constants as constants
import src.routes.route_inference as route_inference
import src.routes.route_stream as route_stream
import src.routes.route_healthcheck as route_healthcheck
import src.restapi.request_middleware as request_middleware
from src.restapi.exception_handlers import exception_handlers_list

from config import (
    model_gpu, 
    DEBUG,
    THREADS_MAX_WORKERS,
    MODEL_ID,
    CONVERT_TOKENS_TO_IDS,
    TORCH_DTYPE
)

# Lets globally load the model

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

# Shared ThreadPoolExecutor
shared_executor = ThreadPoolExecutor(max_workers=THREADS_MAX_WORKERS)

# Dependency injection to routes
async def get_dependencies():
    return {
            "tokenizer": tokenizer, 
            "model": model, 
            "terminators": terminators, 
            "shared_executor": shared_executor
    }

# route_inference handler with dependency injection
async def route_inference_dependencies(request):
    dependencies = await get_dependencies()
    return await route_inference.inference(request, **dependencies)

# route_stream handler with dependency injection
async def route_stream_dependencies(request):
    dependencies = await get_dependencies()
    return await route_stream.stream(request, **dependencies)

# route baseline
base_route = "/v" + palmapy_version

# Create the Starlette application
app = Starlette(
    # Define if we are in debug mode
    debug=DEBUG,

    # Define the routes for the Starlette application
    routes=[
        # Create a route for healthchecks
        Route(base_route + "/healthcheck", request_middleware.options_handler_get, methods=["OPTIONS"]),
        Route(base_route + "/healthcheck", route_healthcheck.healthcheck, methods=["GET"]),
        
        # Create a route for the standard inference, accessible via POST method
        Route(base_route + "/inference", request_middleware.options_handler_post, methods=["OPTIONS"]),
        Route(base_route + "/inference", route_inference_dependencies, methods=["POST"]),
        
        # Create a route for the streaming tokens, accessible via POST method
        Route(base_route + "/stream", request_middleware.options_handler_post, methods=["OPTIONS"]),
        Route(base_route + "/stream", route_stream_dependencies, methods=["POST"]),
    ],

    # Define the middlewares needed
    middleware = [
        Middleware(GZipMiddleware, minimum_size=1000, compresslevel=9),
        Middleware(request_middleware.CustomHeadersMiddleware, headers={
            constants.API_VERSION_HTTP_HEADER_NAME: constants.API_VERSION,

            # Im adding the CORS here, because the standard CORSMiddleware was not working properly
            constants.HEADER_DEFAULT_ACCESS_CONTROL_MAX_AGE: constants.HTTP_DEFAULT_ACCESS_CONTROL_MAX_AGE,
            constants.HEADER_DEFAULT_ACCESS_CONTROL_ALLOW_ORIGIN: constants.HTTP_DEFAULT_ACCESS_CONTROL_ALLOW_ORIGIN,
            constants.HEADER_DEFAULT_ACCESS_CONTROL_ALLOW_HEADERS: constants.HTTP_DEFAULT_ACCESS_CONTROL_ALLOW_HEADERS
        }),
        Middleware(request_middleware.DefaultContentTypeMiddleware, content_type=constants.HTTP_DEFAULT_CONTENT_TYPE),
        Middleware(request_middleware.ValidateContentTypeMiddleware)
    ],

    # Define the exception handlers
    exception_handlers=exception_handlers_list
)
