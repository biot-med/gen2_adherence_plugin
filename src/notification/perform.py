from src.utils.biot_api import update_patient_by_id
from src.utils.configure_logger import logger
from src.utils.generic_success_response import generic_success_response
from src.constants import ADHERENCE_SESSION_TEMPLATE_NAME, DONE, LAST_SESSION_TIME_ATTRIBUTE


def perform(data, token, traceparent, metadata):
    """Perform the action of saving the end time of the session to the patient entity.

    Args:
        data (dict): The incoming data extracted from the event that should contain information about the session.
        token (str): The access token.
        traceparent (str): The traceparent.
        metadata (dict): Metadata extracted from the incoming event.

    Returns:
        dict: A generic success response in case of a successful execution.
    """
    
    logger.debug("Checking if incoming session requires adherence.")
    session_entity = data["entity"]
    if session_entity["_template"]["name"] != ADHERENCE_SESSION_TEMPLATE_NAME or session_entity["_state"] != DONE:
        return generic_success_response(traceparent)
    
    logger.debug("Updating patient last session time.")
    patient_id = session_entity["_patient"]["id"]
    update_payload = {LAST_SESSION_TIME_ATTRIBUTE: session_entity["_endTime"]}
    response = update_patient_by_id(patient_id, update_payload, token, traceparent)
    logger.debug("Response of update patients last session use time.", response)
    return generic_success_response(traceparent)
