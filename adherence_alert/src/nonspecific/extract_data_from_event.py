from src.constants import NO_EVENT_ERROR, NO_DATA_ERROR, JWT_ERROR

def extract_data_from_event (event): 
    return event["body"]
