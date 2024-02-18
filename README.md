# README

# BioT's Adherence Plugin Lambda Seed.

_This is a basic template for an AWS lambda to be used as a starting point for any adherence plugins extending BioT's services._

[Read here](https://docs.biot-med.com/docs/biot-plugins) about BioT plugins. 

This seed works with "_create" and "_update" usage session notification triggers, and with a scheduled non-specific trigger.
The lambda first determines what hook is used and retrieves the relevant functions (using a mapper).
For the lambda to work as is, the hooktype property must be specified in the header sent in the event (except for non-specific lambdas).



### Maintenance Notes
1. All additional dependencies must be compatible with AWS Lambda execution environment as explained in: https://docs.aws.amazon.com/lambda/latest/dg/python-package.html#python-package-native-libraries.
2. Whenever a change is made, the plugin needs to be redeployed using the provided deployment script.

### Cleaning up unwanted code

If you are using the lambda seed for just one hook type, you can remove all folders not relevant for the usage and delete the `check_request_type` and the `functions_mapper` lines, then import the functions normally (with import) directly from the remaining folder. For instance, for interceptorPre, use:

`from src.interceptor_pre.index import authenticate, login, extractDataFromEvent, perform, createErrorResponse`

Unused steps and functions can be removed as well.

### Constants

For running locally you can use local_dev_constants in the constants file.
Just make sure to fill the variables according to the lambda's variables **in the dev environment**

## Supported hooks

- Notifications - notification services
  - hooktype name: `NOTIFICATION`
- Other general lambda types not mentioned above
  - ( hooktype not required but in the code accessed using `NONSPECIFIC` )

## Basic code flow

**This is the lambda's basic flow (see the root index.js file):**

1. These basic functions run at the beginning of the lambda (you can change them as required):

- `check_request_type(event)` - this function checks the hook type from the event. If the lambda has only one usage this can be removed (along with the following functionsMapper).

- `functions_mapper[request_type]` - This contains the functions from the relevant hook type folder. If you use the lambda for just one of the hooks you can import the functions directly from the folder and delete this line.

- `extract_data_from_event` - extract the data, metadata, traceparent and token from the lambda's event (this is diffract for each hook type).

- `traceparent = event_traceparent if event_traceparent is not None else create_traceparent()` - get a traceparent from the event (or fallback to a traceparent from a BioT service)

- `configure_logger` - creating new logs format that follows the structure required for dataDog logs (including a traceId). Environment variable BIOT_SHOULD_VALIDATE_JWT should be false if the lambda does not receive a token, otherwise authentication will fail the lambda

- `authenticate` - authenticate the token sent by the notification service.

- `login` - login the lambda (service user) and get a token

- `perform` - This is where you write your code. The `perform` functions typically call `call_to_api_example` to show an example of calling a BioT service. The interceptors also show an example of changing the data sent in the request/response.
  Note: Not all the argument set to the perform function are relevant for every hook type, so fallbacks are supplied to prevent code errors.
  _Make sure to remove the examples in the lambda and substitute your own._

- `create_error_response` - This is a mapper for errors to be returned from the lambda.
  - In case of interceptors, the data structure is important (follow the data structure supplied for the interceptors in their `create_error_response` function).
  - If you add a new error code, add the error's code name to the constants, add the error response in `create_error_response`, and use `raise Exception(ERROR_CODE_NAME)` where the error occur in your code.

## Deployment
- Copy the "deploy_config.py" file from the "deployment template" folder to the main folder.
- Fill in the required information in the copied "deploy_config.py" file.
- For the first deployment, set "is_initial" to True and "version" to "1". Otherwise, set "is_initial" to False.
- You can add any additional environment variables in the "env_vars" dictionary.
- Run `python scripts/deploy.py`
## Environment variables

**Make sure to define these env variables in your lambda**:

- `BIOT_JWT_PERMISSION_INTERCEPTION` or `BIOT_JWT_PERMISSION_NOTIFICATION` - permissions sent in the token.
  The default for this is a single string - `ACTION_NOTIFICATION` for notifications or `PLUGIN_INTERCEPTOR` for interceptors.

- `BIOT_SERVICE_ENVIRONMENT` - for instance "gen2int"

- `BIOT_SHOULD_VALIDATE_JWT` - This should be false if the service does not need to validate the JWT.

- `LAST_SESSION_TIME_KEY` - The last session time key as it appears in the patient template.

- `ADHERENCE_SESSION_TEMPLATE_NAME` - The template name of the session that requires adherence.

- `ADHERENCE_TIME_IN_DAYS` - Minimum time in days of not doing a session to trigger non-adherence.

- `ALERT_TEMPLATE_NAME` - The template name of the adherence alert.