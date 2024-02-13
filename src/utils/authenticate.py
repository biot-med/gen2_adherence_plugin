import json
from calendar import timegm
from datetime import datetime

import requests
from jose import jws
from jose.constants import ALGORITHMS
from jose.exceptions import ExpiredSignatureError, JWTClaimsError
from src.constants import GET_PUBLIC_KEY_API_URL, JWT_ERROR, JWT_PERMISSION, BIOT_BASE_URL, BIOT_SERVICE_USER_ID, \
    BIOT_SERVICE_USER_SECRET_KEY, TRACEPARENT_KEY


def authenticate(token, traceparent):
    """This validates the token sent by the notification service and checks the required permission.

    Args:
        token (string): The original JWT.
        traceparent (string): traceparent
    """

    try:
        """ 
            This validates the token sent by the notification service and checks the required permission

            This implementation checks JWT_PERMISSION from constants.py.
            You can define it in your plugin's environment variables, see constants.py
        """
        check_jwt(token, traceparent, JWT_PERMISSION)
        return
    except Exception as e:
        raise Exception(JWT_ERROR, {"cause": e})


def login(traceparent):
    """Logs the service user into the BioT system and returns an access token.

    Args:
        traceparent (string): traceparent.

    Returns:
        string: The access token to be used by subsequent requests to the BioT API.
    """

    if BIOT_BASE_URL is None:
        raise Exception("No BIOT_BASE_URL")
    if BIOT_SERVICE_USER_ID is None:
        raise Exception("No BIOT_SERVICE_USER_ID")
    if BIOT_SERVICE_USER_SECRET_KEY is None:
        raise Exception("No BIOT_SERVICE_USER_SECRET_KEY")

    url = BIOT_BASE_URL + "/ums/v2/services/accessToken"
    res = requests.post(
        url,
        json={
            "id": BIOT_SERVICE_USER_ID,
            "secretKey": BIOT_SERVICE_USER_SECRET_KEY,
        },
        headers={
            TRACEPARENT_KEY: traceparent,
        }
    )

    return res.json()["accessToken"]


def get_public_key(traceparent):
    """Gets the public key.

    Args:
        traceparent (string): traceparent.

    Returns:
        string: The public key to be used by the lambda.
    """

    if BIOT_BASE_URL is None:
        raise Exception("No BIOT_BASE_URL")

    url = BIOT_BASE_URL + GET_PUBLIC_KEY_API_URL
    res = requests.get(
        url,
        headers={
            TRACEPARENT_KEY: traceparent,
        }
    )

    return res.json()["publicKey"]


def construct_public_key(public_key_response):
    return "-----BEGIN PUBLIC KEY-----\n" + public_key_response + "\n-----END PUBLIC KEY-----"


def check_jwt(token, traceparent, required_permission=None):
    # This validates the token sent by the notification service
    try:
        public_key_response = get_public_key(traceparent)
        public_key = construct_public_key(public_key_response)

        decoded = jws.verify(token, public_key, ALGORITHMS.RS512)
        claims = json.loads(decoded.decode("utf-8"))

        if "exp" not in claims:
            return claims
        try:
            exp = int(claims["exp"])
        except ValueError:
            raise JWTClaimsError("Expiration Time claim (exp) must be an integer.")
        now = timegm(datetime.utcnow().utctimetuple())
        if exp < now:
            raise ExpiredSignatureError("Signature has expired.")

    except Exception:
        raise Exception(JWT_ERROR)

    if required_permission is None:
        return

    # If you need to, update this function to add other permissions to be checked in the JWT

    # Checks the required permission in the token

    if required_permission not in claims["scopes"]:
        raise Exception(f'JWT does not have the required permissions. Missing: {required_permission}')
