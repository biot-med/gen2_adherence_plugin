import json

from src.index import logger, check_request_type, functions_mapper, BIOT_SHOULD_VALIDATE_JWT, create_traceparent


# This is just an example!
# The structure of the event can be anything

def handler(event, lambda_context=None):
    # The following two logs are just for debugging. You should remove them as soon as you can, the token should not be printed to logs.
    logger.info("At Lambda start, got event: ", event)

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
        # Note: Some of these properties might not be relevant for certain cases, you can remove them if they are not relevant
        #       For example, metadata does not exist in interceptors' events.
        extracted_data = extract_data_from_event(event)
        if "scheduled" in extracted_data and extracted_data["scheduled"] is True:
            traceparent = create_traceparent()
            return perform(None, login(traceparent), traceparent, None)
        
        data = extracted_data["data"] if "data" in extracted_data else None
        event_token = extracted_data["event_token"] if "event_token" in extracted_data else None
        event_traceparent = extracted_data["event_traceparent"] if "event_traceparent" in extracted_data else None
        metadata = extracted_data["metadata"] if "metadata" in extracted_data else None

        # We extract the traceparent from the event
        # As a fallback, if the traceparent is not included, we get a new traceparent from a open BioT AIP service
        traceparent = event_traceparent if event_traceparent is not None else create_traceparent()
        logger.configure_logger(traceparent)

        # This is the authentication process for the lambda itself
        # Note: environment variable BIOT_SHOULD_VALIDATE_JWT should be false if the lambda does not receive a token, otherwise authentication will fail the lambda
        if BIOT_SHOULD_VALIDATE_JWT:
            authenticate(event_token, traceparent)

        # Here we are requesting a token for the lambda
        # It is done using a service users BIOT_SERVICE_USER_ID and BIOT_SERVICE_USER_SECRET_KEY that should be set to an environment variable
        token = login(traceparent)

        # Some of the properties sent to perform might not be relevant, depending on the type of lambda or lambda hook used to invoke it
        response = perform(
            data,
            token,
            traceparent,
            metadata
        )

        return response
    except Exception as e:
        # This should return the proper error responses by the type of error that occurred
        # See the createErrorResponse function for your specific lambda usage
        return create_error_response(e, traceparent)