request_types = {
    "NOTIFICATION": "NOTIFICATION",
    "INTERCEPTOR_PRE": "INTERCEPTOR_PRE",
    "INTERCEPTOR_POST": "INTERCEPTOR_POST",
    "INTERCEPTOR_POST_ENTITY": "INTERCEPTOR_POST_ENTITY",
    "NONSPECIFIC": "NONSPECIFIC"
}

def check_request_type (event):
    """This creates a case-insensitive search for the hooktype by first searching the key in the headers

    Args:
        event (dict): The event.

    Returns:
        string: The request type.
    """
    hooktype_key = list(filter(lambda k: k.lower() == "hooktype", list(event["headers"].keys())))
    hooktype_key = hooktype_key[0] if len(hooktype_key) > 0 else None
  
    if hooktype_key is not None and event["headers"][hooktype_key] in request_types:
        return request_types[event["headers"][hooktype_key]]
    else :
        print("No hooktype provided")
        return request_types["NONSPECIFIC"]
  