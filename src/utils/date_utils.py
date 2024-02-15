from datetime import datetime, timedelta

def iso_date_x_days_ago(days: int):
    """Get ISO formatted string of a date x days ago.

    Args:
        days (int): The number of days ago.

    Returns:
        string: The iso formatted string of a date x days ago.
    """

    return formatted_iso_date(datetime.today() - timedelta(days=days))

def formatted_iso_date(date: datetime):
    """Get ISO formatted string of a date

    Args:
        date (datetime): the datetime to convert to iso string.

    Returns:
        string: The ISO formatted string of the given datetime.
    """

    return date.isoformat("T", "milliseconds") + "Z"

def iso_string_to_datetime(date_str: str):
    """Get datetime from ISO formatted string.

    Args:
        date_str (str): The ISO formatted string that represents a date.

    Returns:
        datetime: The datetime from the ISO formatted string.
    """

    return datetime.fromisoformat(date_str.split(".", 1)[0].replace("Z", ""))