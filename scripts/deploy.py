import os
import subprocess
import shutil
import json
import traceback
from urllib.parse import quote
from distutils import dir_util
import sys

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from deploy_config import env_vars, deploy_vars

BASE_URL = 'https://' + deploy_vars["base_url"]
DEFAULT_PATIENT_TEMPLATE_NAME = 'Patient'
SEARCH_TEMPLATE_BY_FILTER_URL = BASE_URL + '/settings/v1/templates?searchRequest='
LOGIN_URL = BASE_URL + '/ums/v2/users/login'
TEMPLATE_BY_ID_URL = BASE_URL + '/settings/v1/templates/<templateId>'
DEPLOY_URL = BASE_URL + "/settings/v1/plugins"
DIST_PATH = "./dist"
LAST_SESSION_TIME_ATTRIBUTE = env_vars["LAST_SESSION_TIME_ATTRIBUTE"] if "LAST_SESSION_TIME_ATTRIBUTE" in env_vars\
    else "last_session_time"


def clear_artifacts():
    print("Cleaning deployment artifacts.")
    os.remove("./plugin.zip")
    shutil.rmtree(DIST_PATH)

    print("Cleaned deployment artifacts.")


def find_patient_template(headers, requests):
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
        url = f'{SEARCH_TEMPLATE_BY_FILTER_URL}{quote(json.dumps(searchQuery))}'
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


def update_patient_template(patient_template, headers, requests):
    print("Updating patient template")
    try:
        customAttributes = patient_template.get('customAttributes')\
              if patient_template.get('customAttributes') is not None else []
        
        if len(list(filter(lambda e: e["name"] == LAST_SESSION_TIME_ATTRIBUTE, customAttributes))) > 0:
            print("Patient template already has a last session time attribute.")
            return
        
        for attribute in customAttributes:
            if attribute.get("category") is None:
                continue
            attribute["category"] = attribute["category"]["name"]
        
        customAttributes.append({
            "name": LAST_SESSION_TIME_ATTRIBUTE,
            "displayName": "last session time",
            "category": "REGULAR",
            "type": "DATE_TIME",
        })

        template_attributes = patient_template['templateAttributes']
        template_attributes[0]['organizationSelectionConfiguration'] = template_attributes[0]['organizationSelection']
        template_attributes[0]['organizationSelectionConfiguration']['all'] = True
        template_attributes[0]['value'] = ["SELF","ANONYMOUS"]

        update_body = {
            'builtInAttributes': patient_template["builtInAttributes"],
            'templateAttributes': template_attributes,
            'description': patient_template['description'],
            'displayName': patient_template['displayName'],
            'name': patient_template['name'],
            'ownerOrganizationId': patient_template['ownerOrganizationId'],
            'parentTemplateId': patient_template['parentTemplateId'],
            'customAttributes': customAttributes
        }

        id = patient_template['id']
        url = f'{TEMPLATE_BY_ID_URL.replace("<templateId>", id)}'
        res = requests.put(url, headers=headers, json=update_body)
        if res.status_code != 200:
            print("ERROR: can't update Patient template")
            raise Exception(f'{res.status_code}: {res.text}')
    except Exception as e:
        print(e)


def deployment_setup(plugin_name):
    if not os.path.exists(DIST_PATH):
        print("Creating deployment dir.")
        os.makedirs(DIST_PATH)
        print("Created deployment dir.")

    current_directory = os.getcwd()
    print("CWD: " + current_directory)

    print(f"Installing dependencies at deployment dir.")
    subprocess.run(f"pip install -r requirements.txt --target " + DIST_PATH, shell=True)
    print(f"Installed dependencies at deployment dir.")

    print("Copying the plugin into the deployment dir.")
    dir_util._path_created = {} # clear the path cache, so new dir will be created
    dir_util.copy_tree(f'./{plugin_name}/src', DIST_PATH + "/src")
    shutil.copyfile(f'./{plugin_name}/index.py', DIST_PATH + "/index.py")
    print("Successfully copied the plugin into the deployment dir.")

    print("Zipping plugin deployment dir.")
    shutil.make_archive("plugin", 'zip', "./dist")
    print("Successfully zipped plugin deployment dir.")


def create_configuration_payload(plugin_name, plugin_display_name, version, subscribe):
    return {
        "name": plugin_name,
        "displayName": plugin_display_name,
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
                    "entityTypeName":"usage-session",
                    "actionName":"_create"
                },
                {
                    "entityTypeName":"usage-session",
                    "actionName":"_update"
                }
            ]
        } if subscribe else {}
    }

def deploy_plugin_file(plugin_name, plugin_display_name, headers, requests, subscribe):
    deploy_url = DEPLOY_URL
    if deploy_vars["is_initial"]:
        request = requests.post
        version = deploy_vars["version"]
    else:
        request = requests.put
        deploy_url = deploy_url + "/Plugin-" + plugin_name
        print("Fetching the plugin's latest version number.")
        version_res = requests.get(url=deploy_url, headers=headers)
        old_version = int(version_res.json()["version"])
        version = old_version + 1
        print(f"Fetched version. Current version: {old_version}, new version: {version}.")

    print("Deploying plugin.")
    config_payload = create_configuration_payload(plugin_name, plugin_display_name, version, subscribe)

    plugin_zip = open("plugin.zip", "rb")

    deploy_payload = {
        "code": ("plugin.zip", plugin_zip, "gzip, deflate, br"),
        "configuration": json.dumps(config_payload)
    }

    deploy_res = request(url=deploy_url, files=deploy_payload, headers=headers)
    plugin_zip.close()
    print("Deployed plugin with response: ", deploy_res.text)

    clear_artifacts()

def deploy_plugin(plugin_name, plugin_display_name, subscribe):
    print("Deploying " + plugin_name)
    deployment_setup(plugin_name)
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

    patient_template = find_patient_template(headers, requests)
    update_patient_template(patient_template, headers, requests)

    deploy_plugin_file(plugin_name, plugin_display_name, headers, requests, subscribe)

try: 
    print("****BEGIN DEPLOYMENT****")

    deploy_plugin(deploy_vars["session_tracker_plugin_name"], deploy_vars["session_tracker_display_name"], True)
    deploy_plugin(deploy_vars["alert_plugin_name"], deploy_vars["alert_plugin_display_name"], False)

    print("****FINISHED DEPLOYMENT****")

except Exception:
    print("deployment failed with error: ", traceback.format_exc())
    clear_artifacts()
    print("****FAILED DEPLOYMENT****")
