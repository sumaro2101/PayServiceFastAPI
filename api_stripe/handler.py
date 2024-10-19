from stripe import _error


def error_stripe_handle(err: _error.InvalidRequestError) -> str:
    return err.args[0]
