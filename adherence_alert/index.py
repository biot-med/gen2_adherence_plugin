import json

from src.index import logger, check_request_type, functions_mapper, BIOT_SHOULD_VALIDATE_JWT, create_traceparent


# This is just an example!
# The structure of the event can be anything

def handler(event, lambda_context=None):
    # The following two logs are just for debugging. You should remove them as soon as you can, the token should not be printed to logs.
    logger.debug("At Lambda start, got event: ", event)

    traceparent = "traceparent-not-set"

    # This mapper makes it possible to use all types of the lambdas hooks (notification, interceptors or any other non-specific hooks)
    # This requestType can be replaced with spreading the specific functionsMapper for your type of hook, or a direct import of the types functions
    # Then you can remove checkRequestType and the mapper
    # Example: For interceptorPre, you can remove this and at the top of this file add:
    #          import { authenticate, login, extractDataFromEvent, perform, createErrorResponse } from "./src/interceptorPre/index.js"
    request_type = check_request_type(event)

    authenticate = functions_mapper[request_type].authenticate
    login = functions_mapper[request_type].login
    extract_data_from_event = functions_mapper[request_type].extract_data_from_event
    perform = functions_mapper[request_type].perform
    create_error_response = functions_mapper[request_type].create_error_response

    try:
        # This extracts the data, metadata, token and traceparent from the event
        extracted_data = extract_data_from_event(event)
        if "scheduled" in extracted_data and extracted_data["scheduled"] is True:
            print("found scheduled event")
            traceparent = create_traceparent()
            return perform(None, login(traceparent), traceparent, None)

    except Exception as e:
        # This should return the proper error responses by the type of error that occurred
        # See the createErrorResponse function for your specific lambda usage
        return create_error_response(e, traceparent)