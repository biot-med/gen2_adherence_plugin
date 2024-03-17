deploy_vars = {

    "base_url": "<Base url for deployment - can be obtained from the BioT console -> Setting menu -> Technical Information -> Rest API URL>",

    "version": "<Plugin initial version>", # only useful if is_initial is set to True

    "name": "<The name of the plugin>",

    "display_name": "<The display name of the plugin>",

    "is_initial": False, # Is this the first deployment of the plugin under the given name? True/False. On initial deployment the deployment script will create a new plugin. Later it would update an exisitng one.

    "login_username": "<Manufacturer Admin Login username>",

    "login_password": "<Manufacturer Admin Login password>",

    "runtime": "python3.9", # The python runtime on the lambda

    "handler": "index.handler", # The path to the lambda handler <file.function>

    "timeout": 60, # The plugin timeout. The plugin will automatically be terminated it exceeds this timeout

    "memory_size": 128 # The lambda RAM size.  The plugin will automatically be terminated it exceeds this memory size
}

env_vars = {
    "AWS_EXECUTION_ENV": "<Execution environment on AWS>", # set to 'DEV' when deploying in your development environment
    "LAST_SESSION_TIME_ATTRIBUTE": "<The last session time key as it appears in the patient template>",
    "ADHERENCE_SESSION_TEMPLATE_NAME": "<The template name of the session that requires adherence>",
    "ALERT_TEMPLATE_NAME": "<The template name of the adherence alert>",
    # In a similar manner, add the rest of your lambda's environment variables here.
}