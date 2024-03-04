# README

# BioT's Adherence Plugin

The solution is be composed of 2 plugins.  
The first "Last Session Tracker" plugin, will be triggered upon session completion/update, and update the last session timestamp of patient attribute.  
The second "Adherence Alert" plugin, will be executed periodically and get all the patients that did not complete a session in the last X days. Then it will create an alert for each patient.  
Both plugins are deployed under the same function code. When the wrapper function is executed it would trigger the appropriate plugin according to the context.  
BioT notification would trigger the "Last Session Tracker" plugin.  
The scheduler will trigger the "Adherence Alert" plugin.

[Read here](https://docs.biot-med.com/docs/biot-plugins) about BioT plugins.

### Plugin Setup
1. Create a patient alert template for non-adherence alerts.
2. In the organization template, create an attribute of type label called "Adherence Alert Template Name" (json name "adherence_alert_template_name") and set the value to name of the alert template created in the previous step.
3. In the organization template, create an attribute of type integer called "Adherence Time in Days" (json name "adherence_time_in_days"). Set the value to be the minimum time in days for non-adherence.
4. In the patient template, create an attribute named "Last Session Time" of type DATE_TIME. The deployment script will check if this attribute exist and if not, will create one for you.
5. Environment variables must be configured in the deploy config as described in the "Deployment" section below.

### Deployment
The deployment script deploys both plugins under a single function.  
- Copy the "deploy_config.py" file from the "deployment template" folder to the main folder.
- Fill in the required information in the copied "deploy_config.py" file.
- For the first deployment, set "is_initial" to True and "version" to "1". Otherwise, set "is_initial" to False.
- You can add any additional environment variables in the "env_vars" dictionary.
- Run `python scripts/deploy.py`
- A scheduler need to be configured for the alert plugin to work. Contact BioT support for help.

### Maintenance Notes
1. All additional dependencies must be compatible with AWS Lambda execution environment as explained in: https://docs.aws.amazon.com/lambda/latest/dg/python-package.html#python-package-native-libraries.
2. Whenever a change is made, the plugin needs to be redeployed using the provided deployment script.

### Constants
To run locally, you can use local_dev_constants in the constants file.
Just make sure to fill the variables according to the lambda's variables **in the dev environment**

## Plugin Subscriptions 
###Last Session Tracker
- Notifications - notification services
  - hooktype name: `NOTIFICATION`
###Adherence Alert
- Executed by schedualer so no specific subscription 
  - ( hooktype not required but in the code accessed using `NONSPECIFIC` )

## Basic code flow

**This is the lambda's basic flow (see the root index.js file):**

1. These basic functions run at the beginning of the lambda (you can change them as required):

- `check_request_type(event)` - this function checks the hook type from the event. 

- `functions_mapper[request_type]` - This contains the functions from the relevant hook type folder. 

- `extract_data_from_event` - extract the data, metadata, traceparent and token from the lambda's event (this is diffract for each hook type).

- `traceparent = event_traceparent if event_traceparent is not None else create_traceparent()` - get a traceparent from the event (or fallback to a traceparent from a BioT service)

- `configure_logger` - creating new logs format that follows the structure required for dataDog logs (including a traceId). Environment variable BIOT_SHOULD_VALIDATE_JWT should be false if the lambda does not receive a token, otherwise authentication will fail the lambda

- `authenticate` - authenticate the token sent by the notification service.

- `login` - login the lambda (service user) and get a token

- `perform` - This is where the main code of the plugin is written. In notification, the perform checks the session type and status and saves the last session time in the patient entity. In non-specific, the perform runs periodically, fetches all non-adherent patients, and creates a non-adherence alert for them. 

- `create_error_response` - This is a mapper for errors to be returned from the lambda.
  - In case of interceptors, the data structure is important (follow the data structure supplied for the interceptors in their `create_error_response` function).
  - If you add a new error code, add the error's code name to the constants, add the error response in `create_error_response`, and use `raise Exception(ERROR_CODE_NAME)` where the error occur in your code.

## APIs used in the plugins
| Name                 | Type  | URL                                                                                                                                  | Description                       |
|----------------------|-------|--------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------|
| Update Patient       | PATCH | [/organization/v1/users/patients/{id}](https://docs.biot-med.com/reference/updatepatient)                                            | Update the last session timestamp |
| Search Organization  | GET   | [/organization/v1/organizations](https://docs.biot-med.com/reference/searchorganizations)                                            | Get all organizations             |
| Search Patient       | GET   | [/organization/v1/users/patients](https://docs.biot-med.com/reference/searchpatients)                                                | Search for non-adherent patients  |
| Create Patient Alert | POST  | [/organization/v1/users/patients/{patientId}/alerts/{templateName}](https://docs.biot-med.com/reference/createalertbytemplatename-1) | Generate an alert for a patient   |


## Environment variables
**Make sure to define these env variables in your lambda**:

- `BIOT_JWT_PERMISSION_INTERCEPTION` or `BIOT_JWT_PERMISSION_NOTIFICATION` - permissions sent in the token.
  The default for this is a single string - `ACTION_NOTIFICATION` for notifications or `PLUGIN_INTERCEPTOR` for interceptors.

- `BIOT_SERVICE_ENVIRONMENT` - for instance "dev"

- `BIOT_SHOULD_VALIDATE_JWT` - This should be false if the service does not need to validate the JWT.

- `LAST_SESSION_TIME_KEY` - The last session time attribute name as it appears in the patient template.

- `ADHERENCE_SESSION_TEMPLATE_NAME` - The template name of the session that requires adherence.

- `ALERT_TEMPLATE_NAME` - The template name of the adherence alert.