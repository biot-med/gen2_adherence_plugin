from src.constants import API_CALL_ERROR, JWT_ERROR, NO_EVENT_ERROR, NO_DATA_ERROR, BIOT_SERVICE_ENVIRONMENT, BIOT_APP_NAME, TRACEPARENT_KEY
from src.utils.configure_logger import logger
from src.utils.traceparent_utils import parse_traceparent_string

env_fallback = "Not specified"

def build_response_error(status_code, code, message, trace_id, traceparent):
    return {
        "statusCode": status_code,
        "body": {
            "code": code,
            "message": message,
            "serviceName": BIOT_APP_NAME if BIOT_APP_NAME is not None else env_fallback,
            "traceId": trace_id,
            "environment": BIOT_SERVICE_ENVIRONMENT if BIOT_SERVICE_ENVIRONMENT is not None else env_fallback,
            "details": {},
        },
        "headers": {
            TRACEPARENT_KEY: traceparent
        }
    }

def api_error(error, traceparent, trace_id):
    return build_response_error(
        status_code=500,
        code=API_CALL_ERROR,
        message=f"Call to api failed { f': {error}' if error is not None or error != '' else '.' }",
        trace_id=trace_id,
        traceparent=traceparent
    )

def jwt_error(error, traceparent, trace_id):
    return build_response_error(
        status_code=400,
        code=JWT_ERROR,
        message=f"JWT error occurred { f': {error}' if error is not None or error != '' else '.' }",
        trace_id=trace_id,
        traceparent=traceparent
    )

def no_event_error(error, traceparent, trace_id):
    return build_response_error(
        status_code=400,
        code=NO_EVENT_ERROR,
        message="No event sent",
        trace_id=trace_id,
        traceparent=traceparent
    )

def no_data_error(error, traceparent, trace_id):
    return build_response_error(
        status_code=400,
        code=NO_DATA_ERROR,
        message="no data sent in event",
        trace_id=trace_id,
        traceparent=traceparent
    )

def internal_server_error(error, traceparent, trace_id):
    return build_response_error(
        status_code=500,
        code="SERVER ERROR",
        message="internal server error",
        trace_id=trace_id,
        traceparent=traceparent
    )

errors = {
    API_CALL_ERROR: api_error,
    JWT_ERROR: jwt_error,
    NO_EVENT_ERROR: no_event_error,
    NO_DATA_ERROR: no_data_error,
    "internalServerError": internal_server_error
}

def create_error_response (error, traceparent):
    logger.error("Got error: ", error)
    trace_id = parse_traceparent_string(traceparent)
    if error is not None and error in errors:
        return errors[error](error, traceparent, trace_id)
    else:
        return errors["internalServerError"](error, traceparent, trace_id)

