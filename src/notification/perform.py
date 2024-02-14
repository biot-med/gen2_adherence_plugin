from utils.api import get_patient_by_id, update_patient_by_id
from src.utils.configure_logger import logger
from src.utils.generic_success_response import generic_success_response
from constants import ADHERENCE_SESSION_TEMPLATE_NAME, DONE, LAST_SESSION_KEY


def perform(data, token, traceparent, metadata):
    logger.info("Checking if incoming session requires adherence.")
    session_entity = data["entity"]
    if session_entity["_template"]["name"] != ADHERENCE_SESSION_TEMPLATE_NAME or session_entity["_state"] != DONE:
        return generic_success_response(traceparent)
    
    logger.info("Updating patient last session time.")
    patient_id = session_entity["_patient"]["id"]
    patient = get_patient_by_id(patient_id, token, traceparent)
    patient[LAST_SESSION_KEY] = session_entity["_endTime"]
    response = update_patient_by_id(patient_id, patient, token, traceparent)
    logger.info("Response of update patients last session use time.", response)
    return generic_success_response(traceparent)
