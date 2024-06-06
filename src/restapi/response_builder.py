import json
import src.restapi.constants as constants

# Set error response to return to the client
def set_error_response(error_code, override_message):
    if error_code == "invalid_request":
        status_code = 400
        message = "The request was unacceptable, often due to a problem with the request parameters."
        type = constants.ERROR_INVALID_REQUEST
    elif error_code == "invalid_endpoint":
        status_code = 400
        message = "Unrecognized request URL. Please use a valid url endpoint."
        type = constants.ERROR_INVALID_REQUEST
    elif error_code == "resource_missing":
        status_code = 404
        message = "The requested resource was not found."
        type = constants.ERROR_INVALID_REQUEST
    elif error_code == "request_unsupported_method":
        status_code = 405
        message = "This requested method is not allowed."
        type = constants.ERROR_INVALID_REQUEST
    elif error_code == "request_unsupported_media":
        status_code = 415
        message = "Unsupported Media Type. This endpoint requires a Content-Type of application/json"
        type = constants.ERROR_INVALID_REQUEST
    elif error_code == "internal_error":
        status_code = 500
        message = "An unexpected error occurred. Try again later."
        type = constants.ERROR_API
    # Default
    else:
        status_code = 500
        message = "An unexpected error occurred. Try again later."
        type = constants.ERROR_API

    # Lets see if there is a message override the default one 
    if override_message != "":
        message = override_message

    # Lets package it into a json format
    json_data = {
        "error": {
            "code": error_code,
            "message": message,
            "type": type
        }
    }

    # Pretty-print JSON error
    json_error = json.dumps(json_data, indent=4)
    
    return json_error, status_code