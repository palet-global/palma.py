from starlette.responses import Response
import src.restapi.constants as constants
import src.restapi.response_builder as response_builder
from starlette.requests import Request
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

# Lets create a custom exception for invalid Content-Type:
class InvalidContentTypeException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=415, detail=detail)

# Lets check to see if the content type is the one we support 
class ValidateContentTypeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method in ("POST", "PUT", "PATCH"):
            # Note that we parse and normalize the header to remove
		    # any additional parameters (like charset or boundary information) and normalize
		    # it by stripping whitespace and converting to lowercase before we check the value.
            content_type = request.headers.get("content-type")
            content_type = content_type.split(";")[0].strip().lower()
            if content_type != constants.HTTP_DEFAULT_CONTENT_TYPE:
                # You should only raise HTTPException inside routing or endpoints. 
                # Middleware classes should instead just return appropriate responses directly.
                (json_error, status_code) = response_builder.set_error_response("request_unsupported_media", "")

                # Return an json error with status code 415
                return Response(content=json_error, media_type=constants.HTTP_DEFAULT_CONTENT_TYPE, status_code=status_code)
        return await call_next(request)

# Lets create a Middleware for the default content type header 
# If there is no content type header we send the default response
class DefaultContentTypeMiddleware:
    def __init__(self, app, content_type=constants.HTTP_DEFAULT_CONTENT_TYPE):
        self.app = app
        self.content_type = content_type
    
    async def __call__(self, scope, receive, send):
        async def send_wrapper(message):
            if message['type'] == 'http.response.start':
                headers = dict(message['headers'])
                if b'Content-Type' not in headers:
                    headers[b'Content-Type'] = self.content_type.encode('utf-8')
                message['headers'] = list(headers.items())
            await send(message)
        await self.app(scope, receive, send_wrapper)

# Lets create a Middleware for the use of custom values
# You can add multiple headers with this middleware separated by comma
class CustomHeadersMiddleware:
    def __init__(self, app, headers):
        self.app = app
        self.headers = headers

    async def __call__(self, scope, receive, send):
        async def send_wrapper(message):
            if message['type'] == 'http.response.start':
                headers = dict(message['headers'])
                for header_name, header_value in self.headers.items():
                    headers[header_name.encode('utf-8')] = header_value.encode('utf-8')
                message['headers'] = list(headers.items())
            await send(message)
        
        await self.app(scope, receive, send_wrapper)

# Options handlers for the different methods

# Options handlers for GET
async def options_handler_get(request):
    headers = {
        "Access-Control-Allow-Methods": "GET, OPTIONS"
    }
    return Response(status_code=204, headers=headers)

# Options handlers for POST
async def options_handler_post(request):
    headers = {
        "Access-Control-Allow-Methods": "POST, OPTIONS"
    }
    return Response(status_code=204, headers=headers)