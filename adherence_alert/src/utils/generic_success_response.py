from src.constants import TRACEPARENT_KEY


def generic_success_response(traceparent):
    return {
        "statusCode": 200,
        "headers": {
            TRACEPARENT_KEY: traceparent,
        }
    }
