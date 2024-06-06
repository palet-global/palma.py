import json
import src.utils.validators as validators
import src.restapi.response_builder as response_builder

# Process JSON Requests
# Check for valid messages and valid json body
# returns (json_data, json_error, status_code)
async def read_json_request(request):
    # Retrieve and parse the JSON body of the request asynchronously
    try:
        json_data = await request.json()

        # Lets validate the messages format and that is not empty
        if not validators.is_valid_messages(json_data.get("messages", "")) or validators.is_empty(json_data.get("messages", "")):
            # Json error
            (json_error, status_code) = response_builder.set_error_response("invalid_request", "The request was unacceptable, the parameter `messages` structure is not valid or its empty.")

            # Return an json error with status code 400
            return ("", json_error, status_code)
    except json.JSONDecodeError as e:
        # Json error
        (json_error, status_code) = response_builder.set_error_response("invalid_request", "The request was unacceptable, the json body is not valid.")

        # Debug
        print(f"JSONDecodeError: {e}")

        # Return an json error with status code 400
        return ("", json_error, status_code)
    
    # If everything works, return the data
    return (json_data, "", 200)