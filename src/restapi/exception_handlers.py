import src.restapi.constants as constants
import src.restapi.response_builder as response_builder
import src.restapi.request_middleware as request_middleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.exceptions import HTTPException

# Define an asynchronous function to handle 404 Not Found errors
async def not_found(request: Request, exc: HTTPException):
    """
    Return an HTTP 404 page.
    """
    # Json error
    (json_error, status_code) = response_builder.set_error_response("resource_missing", "")

    # Return an json error with status code 404
    return Response(content=json_error, media_type=constants.HTTP_DEFAULT_CONTENT_TYPE, status_code=status_code)

# Define an asynchronous function to handle 405 Method Not Allowed errors
async def method_not_allowed(request: Request, exc: HTTPException):
    """
    Return an HTTP 405 page.
    """
    # Json error
    (json_error, status_code) = response_builder.set_error_response("request_unsupported_method", "")

    # Return an json error with status code 405
    return Response(content=json_error, media_type=constants.HTTP_DEFAULT_CONTENT_TYPE, status_code=status_code)

# Define an asynchronous function to handle 500 Internal Server errors
async def server_error(request: Request, exc: HTTPException):
    """
    Return an HTTP 500 page.
    """
    # Json error
    (json_error, status_code) = response_builder.set_error_response("internal_error", "")

    # Return an json error with status code 500
    return Response(content=json_error, media_type=constants.HTTP_DEFAULT_CONTENT_TYPE, status_code=status_code)

# Define exception handlers for the application
exception_handlers_list = {
    # Handler for 404 Not Found errors
    404: not_found,
    # Handler for 405 Method Not Allowed
    405: method_not_allowed,
    # Handler for 500 Internal Server errors
    500: server_error
}