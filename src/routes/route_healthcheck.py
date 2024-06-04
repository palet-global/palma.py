import json
import src.restapi.constants as constants
from datetime import datetime, timezone
from starlette.responses import Response
from version import palmapy_version

async def healthcheck(request):
    # Json data
    json_data = {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": palmapy_version
    }

    # Pretty-print JSON
    json_pretty = json.dumps(json_data, indent=4)

    # Return the output as a JSON response
    return Response(content=json_pretty, media_type=constants.HTTP_DEFAULT_CONTENT_TYPE, status_code=200)