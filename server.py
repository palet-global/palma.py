from version import palmapy_version
import src.ai.model_load as model_load

from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.applications import Starlette
from starlette.middleware.gzip import GZipMiddleware

import src.restapi.constants as constants
import src.routes.route_inference as route_inference
import src.routes.route_stream as route_stream
import src.routes.route_healthcheck as route_healthcheck
import src.restapi.request_middleware as request_middleware
from src.restapi.exception_handlers import exception_handlers_list

from config import (
    DEBUG
)

# Lets globally load the model
model_dependencies = model_load.init()

# route baseline
base_route = "/v" + palmapy_version

# route_inference handler with dependency injection
async def route_inference_dependencies(request):
    return await route_inference.inference(request, **model_dependencies)

# route_stream handler with dependency injection
async def route_stream_dependencies(request):
    return await route_stream.stream(request, **model_dependencies)

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
