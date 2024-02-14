import json
from urllib.parse import quote

from src.constants import BIOT_BASE_URL, LAST_SESSION_KEY
from src.utils import http_utils


# This is a call to a BioT API, it can be any call provided the lambda service user has permission
def call_api_example(token, traceparent):
    """ This get request asks for patients from organization API.

    Args:
        token (string): JWT for the authorization header.
        traceparent (string): The traceparent.

    Returns:
        dict: empty dict or list of patients.
    """

    url = f"{BIOT_BASE_URL}/organization/v1/users/patients"
    return http_utils.get(url, traceparent, token, body={})

def get_patient_by_id(patient_id, token, traceparent):
    url = f"{BIOT_BASE_URL}/organization/v1/users/patients/{patient_id}"
    return http_utils.get(url, traceparent, token, body={})

def update_patient_by_id(patient_id, payload, token, traceparent):
    url = f"{BIOT_BASE_URL}/organization/v1/users/patients/{patient_id}"
    return http_utils.patch(url, traceparent, token, payload)

def get_all_organizations(token, traceparent):
    filter_dict = {
        "filter": {},
        "limit": 100000000
    }
    url = f"{BIOT_BASE_URL}/organization/v1/organizations?searchRequest={quote(json.dumps(filter_dict))}"
    return http_utils.get(url, traceparent, token, body={})["data"]

def paginate_non_adherent_patients_by_org(org_id, required_last_time, page, limit, token, traceparent):
    filter_dict = {
        "filter": {
            "_ownerOrganization.id": {
                "eq": org_id
            },
            LAST_SESSION_KEY: {
                "to": required_last_time
            }
        },
        "limit": limit,
        "page": page
    }
    url = f"{BIOT_BASE_URL}/organization/v1/users/patients?searchRequest={quote(json.dumps(filter_dict))}"
    return http_utils.get(url, traceparent, token, body={})["data"]

def paginate_new_non_adherent_patients_by_org(org_id, required_last_time, page, limit, token, traceparent):
    filter_dict = {
        "filter": {
            "_ownerOrganization.id": {
                "eq": org_id
            },
            LAST_SESSION_KEY: {
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

    url = f"{BIOT_BASE_URL}/organization/v1/users/patients/{patient_id}/alerts/{template_name}"
    return http_utils.post(url, traceparent, token, body={})