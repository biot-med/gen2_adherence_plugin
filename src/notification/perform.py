from utils.api import call_api_example, get_patient_by_id, update_patient_by_id
from src.utils.configure_logger import logger
from src.utils.generic_success_response import generic_success_response
from constants import ADHERENCE_SESSION_TEMPLATE_NAME, DONE, LAST_SESSION_KEY


def perform(data, token, traceparent, metadata):
    # -----------------------------------------------------------------------------------------
    session_entity = data["entity"]
    if session_entity["_template"]["name"] != ADHERENCE_SESSION_TEMPLATE_NAME or session_entity["_state"] != DONE:
        return generic_success_response(traceparent)
    
    patient_id = session_entity["_patient"]["id"]
    patient = get_patient_by_id(patient_id, token, traceparent)
    patient[LAST_SESSION_KEY] = session_entity["_endTime"]
    update_patient_by_id(patient_id, patient, token, traceparent)

    call_example_response = call_api_example(token, traceparent)

    # In this example you perform your logic with the response Here

    logger.info("In notification lambda, got callExampleResponse ", call_example_response)

    # -----------------------------------------------------------------------------------------
    return generic_success_response(traceparent)
