from src.utils.configure_logger import logger
from src.utils.generic_success_response import generic_success_response

def perform(data, token, traceparent, metadata):
    # -----------------------------------------------------------------------------------------

    # TODO: ADD YOUR CODE HERE !
    # Remove this example call and add your code instead

    logger.info("In nonspecific lambda, some action was performed!")

    # Return your response here (replace genericSuccessResponse with your response)
    return generic_success_response(traceparent)

    # -----------------------------------------------------------------------------------------
