import os

API_CALL_ERROR = "CALL_TO_API_FAILED"
JWT_ERROR = "JWT_ERROR"
NO_EVENT_ERROR = "NO_EVENT"
NO_METADATA_ERROR = "NO_METADATA"
NO_DATA_ERROR = "NO_DATA"
TRACEPARENT_KEY = "traceparent"
GET_PUBLIC_KEY_API_URL = "/ums/v1/security/public-key"
DONE = "DONE"
PAGE_SIZE = 100


def resolve_should_validate(env_var):
    if env_var is not None:
        if env_var == "False" or env_var == "false":
            return False
        else:
            return True
    return True


cloud_constants = {
    "BIOT_APP_NAME": os.getenv("BIOT_APP_NAME"),
    "BIOT_BASE_URL": os.getenv("BIOT_BASE_URL"),
    "BIOT_SERVICE_USER_ID": os.getenv("BIOT_SERVICE_USER_ID"),
    "BIOT_SERVICE_USER_SECRET_KEY": os.getenv("BIOT_SERVICE_USER_SECRET_KEY"),
    "AWS_EXECUTION_ENV": os.getenv("AWS_EXECUTION_ENV"),
    "BIOT_SHOULD_VALIDATE_JWT": resolve_should_validate(os.getenv("BIOT_SHOULD_VALIDATE_JWT")),
    "BIOT_SERVICE_ENVIRONMENT": os.getenv("BIOT_SERVICE_ENVIRONMENT"),
    "HOOKTYPE_PERMISSIONS": {
        "notification": os.getenv("BIOT_JWT_PERMISSION_NOTIFICATION"),
    },
    "JWT_PERMISSION": os.getenv("JWT_PERMISSION"),
    "ADHERENCE_SESSION_TEMPLATE_NAME": os.getenv("ADHERENCE_SESSION_TEMPLATE_NAME"),
    "ADHERENCE_TIME_IN_DAYS": os.getenv("ADHERENCE_TIME_IN_DAYS"),
    "ALERT_TEMPLATE_NAME": os.getenv("ALERT_TEMPLATE_NAME"),
    "LAST_SESSION_TIME_KEY": os.getenv("LAST_SESSION_TIME_KEY") if os.getenv("LAST_SESSION_TIME_KEY") is not None\
        else "last_session_time"
}

local_dev_constants = {
    "BIOT_APP_NAME": "BioT Lambda seed",
    "BIOT_BASE_URL": None,
    "BIOT_SERVICE_USER_ID": None,
    "BIOT_SERVICE_USER_SECRET_KEY": None,
    "AWS_EXECUTION_ENV": "DEV",
    "BIOT_SHOULD_VALIDATE_JWT": None,
    "BIOT_SERVICE_ENVIRONMENT": "int",
    "HOOKTYPE_PERMISSIONS": {
        "notification": "ACTION_NOTIFICATION",
        "interceptorPost": "PLUGIN_INTERCEPTOR",
        "interceptorPre": "PLUGIN_INTERCEPTOR",
        "interceptorPostEntity": "PLUGIN_INTERCEPTOR"
    },
    "JWT_PERMISSION": None,
    "ADHERENCE_SESSION_TEMPLATE_NAME": None,
    "ADHERENCE_TIME_IN_DAYS": None,
    "ALERT_TEMPLATE_NAME": None,
    "LAST_SESSION_TIME_KEY": "last_session_time"
}

default_headers = {
    "User-Agent": "PythonPlugin/1.0.0",
    "Host": "lambda.aws.com",
    "Accept": "application/json",
    "Content-Type": "application/json; charset=utf-8",
}

environment_constants = cloud_constants if os.getenv("AWS_EXECUTION_ENV") is not None else local_dev_constants

JWT_PERMISSION = environment_constants["JWT_PERMISSION"]
BIOT_APP_NAME = environment_constants["BIOT_APP_NAME"]
BIOT_BASE_URL = environment_constants["BIOT_BASE_URL"]
BIOT_SERVICE_USER_ID = environment_constants["BIOT_SERVICE_USER_ID"]
BIOT_SERVICE_USER_SECRET_KEY = environment_constants["BIOT_SERVICE_USER_SECRET_KEY"]
AWS_EXECUTION_ENV = environment_constants["AWS_EXECUTION_ENV"]
BIOT_SHOULD_VALIDATE_JWT = environment_constants["BIOT_SHOULD_VALIDATE_JWT"]
BIOT_SERVICE_ENVIRONMENT = environment_constants["BIOT_SERVICE_ENVIRONMENT"]
HOOKTYPE_PERMISSIONS = environment_constants["HOOKTYPE_PERMISSIONS"]
ADHERENCE_SESSION_TEMPLATE_NAME = environment_constants["ADHERENCE_SESSION_TEMPLATE_NAME"]
ADHERENCE_TIME_IN_DAYS = environment_constants["ADHERENCE_TIME_IN_DAYS"]
ALERT_TEMPLATE_NAME = environment_constants["ALERT_TEMPLATE_NAME"]
LAST_SESSION_TIME_KEY = environment_constants["LAST_SESSION_TIME_KEY"]
