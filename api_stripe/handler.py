from datetime import datetime
from stripe import _error


def error_stripe_handle(err: _error.InvalidRequestError) -> str:
    return err.args[0]


def convert_date_to_unix_time(time: datetime) -> int:
    """
    Конвертация date time в unix секунды
    """
    return int(time.timestamp())
