from src.utils.configure_logger import logger
from src.utils.generic_success_response import generic_success_response
from src.utils.api import get_all_organizations, paginate_non_adherent_patients_by_org,\
    paginate_new_non_adherent_patients_by_org, create_patient_alert
from src.utils.date_utils import iso_date_x_days_ago, iso_string_to_datetime
from src.constants import PAGE_SIZE

def perform(data, token, traceparent, metadata):
    """Fetch and alert non-adherent patients according to the adherence parameters of their related organization.

    Args:
        data (dict): This will always be None because this action runs periodically without an event.
        token (str): The access token.
        traceparent (str): The traceparent.
        metadata (dict): Also will always be None.

    Returns:
        dict: A generic success response in case of a successful execution.
    """    

    logger.info("Get all organizations and cache their adherence parameters into a map.")
    organizations = get_all_organizations(token, traceparent)
    organizations_map = {}
    for org in organizations:
        if org.get("adherence_time_in_days") is not None and org.get("adherence_alert_template_name") is not None:
            organizations_map[org["_id"]] = {
                "adherence_time_in_days": org["adherence_time_in_days"],
                "adherence_alert_template_name": org["adherence_alert_template_name"]
            }
    logger.info(f"Mapped the adherence parameters of {len(organizations_map.keys())} organizations.")

    logger.info("Fetching non-adherent patients of every relevant org and creating patient alerts.")
    for id in organizations_map.keys():
        adherence_time_in_days = iso_string_to_datetime(organizations_map[id]["adherence_time_in_days"])
        required_last_time = iso_date_x_days_ago(adherence_time_in_days)
        alert_template_name = organizations_map[id]["adherence_alert_template_name"]

        create_alerts_for_patients(id, required_last_time, alert_template_name, token, traceparent)
        create_alerts_for_patients(id, required_last_time, alert_template_name, token, traceparent, new_patients=True)
        
    return generic_success_response(traceparent)

def create_alerts_for_patients(org_id, required_last_time, alert_template_name,\
                               token, traceparent, new_patients = False):
    """Fetch non-adherent patients by organization id and its non-adherence period and create alerts for them.

    Args:
        org_id (str): The id of the organization by which to fetch the non-adherent patients.
        required_last_time (str): ISO formatted date. Every patient with a
          last session time older than that is considered non-adherent.
        alert_template_name (str): The template name of the non adherence alerts.
        token (str): The access token.
        traceparent (str): The traceparent.
        new_patients (bool, optional): Either fetch old patients with a last session time older than the
          given threshold, or fetch new patients that haven't had a session yet, but were created before the threshold.
          Defaults to False.
    """

    # Choose whether to paginate old or new non-adherent patients according to the given flag.
    pagination_func = paginate_non_adherent_patients_by_org
    if new_patients:
        pagination_func = paginate_new_non_adherent_patients_by_org

    # Paginate non-adherent patients in chunks configured by PAGE_SIZE and create alerts for them
    page = 0
    while True:
        patients = pagination_func(org_id, required_last_time, page, PAGE_SIZE, token, traceparent)
        for patient in patients:
            create_patient_alert(patient["_id"], alert_template_name, token, traceparent)
        if len(patients) != PAGE_SIZE: #If the fetched page isn't fully populated then it's the last one.
            break
        page += 1