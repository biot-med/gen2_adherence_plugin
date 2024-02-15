import os
import subprocess
import shutil
import json
import traceback
from urllib.parse import quote
from distutils.dir_util import copy_tree
from deploy_config import env_vars, deploy_vars

BASE_URL = 'https://' + env_vars["base_url"]
DEFAULT_PATIENT_TEMPLATE_NAME = 'Patient'
SEATCH_TEMPLATE_BY_FILTER_URL = BASE_URL + '/settings/v1/templates?searchRequest='
LOGIN_URL = BASE_URL + '/ums/v2/users/login'
TEMPLATE_BY_ID_URL = BASE_URL + '/settings/v1/templates/<templateId>'
DEPLOY_URL = BASE_URL + "/settings/v1/plugins"
DIST_PATH = "./dist"
LAST_SESSION_TIME_KEY = env_vars.get("LAST_SESSION_TIME_KEY") if env_vars.get("LAST_SESSION_TIME_KEY") is not None\
    else "last_session_time"


def clear_artifacts():
    print("Cleaning deployment artifacts.")
    os.remove("./plugin.zip")
    shutil.rmtree(DIST_PATH)
    print("Cleaned deployment artifacts.")


def find_patient_template(headers):
    print("Search for default patient template by name " + str(DEFAULT_PATIENT_TEMPLATE_NAME))
    try:
        searchQuery = {
        "filter": {
                "name": {
                    "eq": DEFAULT_PATIENT_TEMPLATE_NAME
                }
            },
            "limit": 1,
            "page": 0
        }
        url = f'{SEATCH_TEMPLATE_BY_FILTER_URL}{quote(json.dumps(searchQuery))}'
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            data = res.json()['data']
            if len(data) > 0:
                print('Default patient template found')
                return data[0]
            raise Exception('Patient template list is empty.')
        else:
            print('Patient template not found.')
            raise Exception(f'{res.status_code}: {res.text}')
    except Exception as e:
        print(e)


def update_patient_template(patient_template, headers):
    print("Updating patient template")
    try:
        customAttributes = patient_template.get('customAttributes')\
              if patient_template.get('customAttributes') is not None else []
        
        if len(filter(lambda e: e["name"] == LAST_SESSION_TIME_KEY, customAttributes)) > 0:
            print("Patient template already has a last session time attribute.")
            return
        
        customAttributes.append({
            "name": LAST_SESSION_KEY,
            "displayName": "last session time",
            "category": "Adherence",
            "type": "DATE_TIME",
        })

        patient_template["customAttributes"] = customAttributes
        id = patient_template['id']
        url = f'{TEMPLATE_BY_ID_URL.replace("<templateId>", id)}'
        res = requests.put(url, headers=headers, body=patient_template)
        if res.status != 200:
            print("ERROR: can't update Patient template")
            raise Exception(f'{res.status_code}: {res.text}')
    except Exception as e:
        print(e)


def deployment_setup():
    if not os.path.exists(DIST_PATH):
        print("Creating deployment dir.")
        os.makedirs(DIST_PATH)
        print("Created deployment dir.")

    print(f"Installing dependencies at deployment dir.")
    subprocess.run(f"pip install -r requirements.txt --target ./dist", shell=True)
    print(f"Installed dependencies at deployment dir.")

    print("Copying the plugin into the deployment dir.")
    copy_tree('./src', DIST_PATH)
    shutil.copyfile("./index.py", DIST_PATH + "/index.py") 
    print("Successfully copied the plugin into the deployment dir.")

    print("Zipping plugin deployment dir.")
    shutil.make_archive("plugin", 'zip', "./dist")
    print("Successfully zipped plugin deployment dir.")


def create_configuration_payload():
    return {
        "name": deploy_vars["name"],
        "displayName": deploy_vars["display_name"],
        "version": version,
        "runtime": deploy_vars["runtime"],
        "timeout": deploy_vars["timeout"],
        "memorySize": deploy_vars["memory_size"],
        "handler": deploy_vars["handler"],
        "environmentVariables": env_vars,
        "subscriptions":{
            "interceptionOrder":"1",
            "notifications":[
                {
                    "entityTypeName":"generic-entity",
                    "actionName":"_create"
                }
            ]
        }
    }


try: 
    print("****BEGIN DEPLOYMENT****")

    deployment_setup()

    from dist import requests

    print("Logging in and getting deployment access token.")

    login_payload = {
        "username": deploy_vars["login_username"],
        "password": deploy_vars["login_password"]
    }

    login_res = requests.post(url=LOGIN_URL, json=login_payload)
    access_token = login_res.json()["accessJwt"]["token"]
    print("Successfully logged in and got deployment access token.")

    headers = {
        "authorization": "Bearer " + access_token
    }


    patient_template = find_patient_template(headers)
    update_patient_template(patient_template, headers)

    deploy_url = DEPLOY_URL

    if deploy_vars["is_initial"]:
        request = requests.post
        version = deploy_vars["version"]
    else:
        request = requests.put
        deploy_url = deploy_url + "/Plugin-" + deploy_vars["name"]
        print("Fetching the plugin's latest version number.")
        version_res = requests.get(url=deploy_url, headers=headers)
        old_version = int(version_res.json()["version"])
        version = old_version + 1
        print(f"Fetched version. Current version: {old_version}, new version: {version}.")

    print("Deploying plugin.")
    config_payload = create_configuration_payload()

    plugin_zip = open("plugin.zip", "rb")

    deploy_payload = {
        "code": ("plugin.zip", plugin_zip, "gzip, deflate, br"),
        "configuration": json.dumps(config_payload)
    }

    deploy_res = request(url=deploy_url, files=deploy_payload, headers=headers)
    plugin_zip.close()
    print("Deployed plugin with response: ", deploy_res.text)

    clear_artifacts()
    print("****FINISHED DEPLOYMENT****")

except Exception:
    print("deployment failed with error: ", traceback.format_exc())
    clear_artifacts()
    print("****FAILED DEPLOYMENT****")
