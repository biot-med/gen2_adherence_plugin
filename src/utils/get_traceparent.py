from secrets import token_bytes

# This is a fallback incase there was no traceparent.
# If it does not exist, it creates a traceparent as a fallback.
# The lambdas creator should implement the creation/fetching of a traceId

def get_traceparent():
    """Get traceparent.

    Returns:
        string: trace_id
    """

    version = '00'
    trace_id = bytes.hex(token_bytes(16))
    id = bytes.hex(token_bytes(8))
    flags = '01'

    return f'{version}-{trace_id}-{id}-{flags}'