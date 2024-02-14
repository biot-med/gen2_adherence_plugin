from src.utils.configure_logger import logger
from src.utils.generic_success_response import generic_success_response
from src.utils.api import get_all_organizations, paginate_non_adherent_patients_by_org,\
    paginate_new_non_adherent_patients_by_org, create_patient_alert
from src.utils.date_utils import iso_date_x_days_ago, iso_string_to_datetime
from src.constants import PAGE_SIZE

def perform(data, token, traceparent, metadata):
    # -----------------------------------------------------------------------------------------

    # TODO: ADD YOUR CODE HERE !
    # Remove this example call and add your code instead

    organizations = get_all_organizations(token, traceparent)
    organizations_map = {}
    for org in organizations:
        if org.get("adherence_time_in_days") is not None and org.get("adherence_alert_template_name") is not None:
            organizations_map[org["_id"]] = {
                "adherence_time_in_days": org["adherence_time_in_days"],
                "adherence_alert_template_name": org["adherence_alert_template_name"]
            }

    for id in organizations_map.keys():
        adherence_time_in_days = iso_string_to_datetime(organizations_map[id]["adherence_time_in_days"])
        required_last_time = iso_date_x_days_ago(adherence_time_in_days)
        alert_template_name = organizations_map[id]["adherence_alert_template_name"]

        create_alerts_for_patients(id, required_last_time, alert_template_name, token, traceparent)
        create_alerts_for_patients(id, required_last_time, alert_template_name, token, traceparent, new_patients=True)
        

    logger.info("In nonspecific lambda, some action was performed!")

    # Return your response here (replace genericSuccessResponse with your response)
    return generic_success_response(traceparent)

    # -----------------------------------------------------------------------------------------

def create_alerts_for_patients(org_id, required_last_time, alert_template_name,\
                               token, traceparent, new_patients = False):
    pagination_func = paginate_non_adherent_patients_by_org
    if new_patients:
        paginate_new_non_adherent_patients_by_org

    while True:
        patients = pagination_func(org_id, required_last_time, 0, PAGE_SIZE, token, traceparent)
        for patient in patients:
            create_patient_alert(patient["_id"], alert_template_name, token, traceparent)
        if len(patients) != PAGE_SIZE:
            break