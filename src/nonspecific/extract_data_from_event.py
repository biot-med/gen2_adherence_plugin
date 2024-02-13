import json
from src.constants import NO_EVENT_ERROR, NO_DATA_ERROR, JWT_ERROR

def extract_data_from_event (event): 
    if event is None:
        raise Exception(NO_EVENT_ERROR)

    parsed_event = json.loads(event["body"])

    if parsed_event is None:
        raise Exception(NO_DATA_ERROR)

    return {
        "data": parsed_event["data"] if "data" in parsed_event else None
    }

