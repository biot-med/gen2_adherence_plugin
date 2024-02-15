deploy_vars = {

    "base_url": "<Base url for deployment>",

    "version": "<Plugin version>", # only useful if is_initial is set to True

    "name": "<The name of the plugin>",

    "display_name": "<The display name of the plugin>",

    "is_initial": False, # Is this the first deployment of the plugin under the given name? True/False

    "login_username": "<Login username>",

    "login_password": "<Login password>",

    "runtime": "python3.9", # The python runtime on the lambda

    "handler": "index.handler", # The path to the lambda handler <file.function>

    "timeout": 60, # The lambda timeout

    "memory_size": 128 # The lambda RAM size
}

env_vars = {

    "AWS_EXECUTION_ENV": "<Execution environment on AWS>",
    "LAST_SESSION_TIME_KEY": "last_session_time",
    # In a similar manner, add the rest of your lambda's environment variables here.

}