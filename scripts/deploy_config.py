deploy_vars = {

    "base_url": "<Base url for deployment - can be obtained from the BioT console -> Setting menu -> Technical Information -> Rest API URL>",

    "version": "1", # only useful if is_initial is set to True

    "alert_plugin_name": "adherence_alert",

    "session_tracker_plugin_name": "last_session_tracker",

    "alert_plugin_display_name": "Adherence Alert",

    "session_tracker_display_name": "Last Session Tracker",

    "is_initial": True, # Is this the first deployment of the plugin under the given name? True/False. On initial deployment the deployment script will create a new plugin. Later it would update an exisitng one.

    "login_username": "<Manufacturer Admin Login username>",

    "login_password": "<Manufacturer Admin Login password>",

    "runtime": "python3.9", # The python runtime on the lambda

    "handler": "index.handler", # The path to the lambda handler <file.function>

    "timeout": 60, # The plugin timeout. The plugin will automatically be terminated it exceeds this timeout

    "memory_size": 128 # The lambda RAM size.  The plugin will automatically be terminated it exceeds this memory size
}

env_vars = {
    "AWS_EXECUTION_ENV": "DEV", # set to 'DEV' when deploying in your development environment
    "LAST_SESSION_TIME_ATTRIBUTE": "<The last session time key as it appears in the patient template>",
    "ADHERENCE_SESSION_TEMPLATE_NAME": "<The template name of the session that requires adherence>",
    "ALERT_TEMPLATE_NAME": "<The template name of the adherence alert>",
    # In a similar manner, add the rest of your lambda's environment variables here.
}