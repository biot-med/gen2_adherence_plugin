from src.constants import JWT_ERROR, HOOKTYPE_PERMISSIONS
from src.utils.authenticate import check_jwt


def authenticate(token, traceparent):
    try:

        requiredPermission = HOOKTYPE_PERMISSIONS["notification"]

        # This validates the token sent by the notification service and checks the required permission
        check_jwt(token, traceparent, requiredPermission)
    
        return
    except Exception as e:
        raise Exception(JWT_ERROR, { "cause": e })