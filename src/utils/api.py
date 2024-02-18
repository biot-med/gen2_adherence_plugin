import json
from urllib.parse import quote

from src.constants import BIOT_BASE_URL, LAST_SESSION_TIME_KEY
from src.utils import http_utils

def get_patient_by_id(patient_id, token, traceparent):
    """Get a patient by their id.

    Args:
        patient_id (str): The patient's id.
        token (str): The access token.
        traceparent (str): The traceparent.

    Returns:
        dict: The fetched patient entity.
    """

    url = f"{BIOT_BASE_URL}/organization/v1/users/patients/{patient_id}"
    return http_utils.get(url, traceparent, token, body={})

def update_patient_by_id(patient_id, payload, token, traceparent):
    """Update a patient by their id.

    Args:
        patient_id (str): The patient's id.
        payload (dict): The update payload.
        token (str): The access token.
        traceparent (str): The traceparent.

    Returns:
        dict: The json parsed response from the update patient API call.
    """

    url = f"{BIOT_BASE_URL}/organization/v1/users/patients/{patient_id}"
    return http_utils.patch(url, traceparent, token, payload)

def get_all_organizations(token, traceparent):
    """Get all organizations.

    Args:
        token (str): The access token.
        traceparent (str): The traceparent.

    Returns:
        list: A list of all found organizations if successful.
    """

    filter_dict = {
        "filter": {},
        "limit": 100000000
    }
    url = f"{BIOT_BASE_URL}/organization/v1/organizations?searchRequest={quote(json.dumps(filter_dict))}"
    return http_utils.get(url, traceparent, token, body={})["data"]

def paginate_non_adherent_patients_by_org(org_id, required_last_time, page, limit, token, traceparent):
    """Paginate non adherent patients of an org.

    Args:
        org_id (str): The organization id.
        required_last_time (str): ISO formatted date representing the threshold for non-adherence.
        page (int): The page number.
        limit (int): The limit per page.
        token (str): The access token.
        traceparent (str): The traceparent.

    Returns:
        list: The fetched non-adherent patients.
    """

    filter_dict = {
        "filter": {
            "_ownerOrganization.id": {
                "eq": org_id
            },
            LAST_SESSION_TIME_KEY: {
                "to": required_last_time
            }
        },
        "limit": limit,
        "page": page
    }
    url = f"{BIOT_BASE_URL}/organization/v1/users/patients?searchRequest={quote(json.dumps(filter_dict))}"
    return http_utils.get(url, traceparent, token, body={})["data"]

def paginate_new_non_adherent_patients_by_org(org_id, required_last_time, page, limit, token, traceparent):
    """Paginate newly-created non adherent patients of an org.

    Args:
        org_id (str): The organization id.
        required_last_time (str): ISO formatted date representing the threshold for non-adherence.
        page (int): The page number.
        limit (int): The limit per page.
        token (str): The access token.
        traceparent (str): The traceparent.

    Returns:
        list: The fetched newly-created non-adherent patients.
    """

    filter_dict = {
        "filter": {
            "_ownerOrganization.id": {
                "eq": org_id
            },
            LAST_SESSION_TIME_KEY: {
                "isNull": True
            },
            "_creationTime": {
                "to": required_last_time
            }
        },
        "limit": limit,
        "page": page
    }
    url = f"{BIOT_BASE_URL}/organization/v1/users/patients?searchRequest={quote(json.dumps(filter_dict))}"
    return http_utils.get(url, traceparent, token, body={})["data"]

def create_patient_alert(patient_id, template_name, token, traceparent):
    """Create an alert with the given template name for a patient with the given patient id.

    Args:
        patient_id (str): The patient id.
        template_name (str): The alert template name.
        token (str): The access token.
        traceparent (str): The traceparent.

    Returns:
        dict: Response from the create patient API call.
    """

    url = f"{BIOT_BASE_URL}/organization/v1/users/patients/{patient_id}/alerts/{template_name}"
    return http_utils.post(url, traceparent, token, body={})