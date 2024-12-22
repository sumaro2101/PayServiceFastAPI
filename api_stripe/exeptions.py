class ErrorTypeProductStripe(Exception):
    """
    Исключение не правильного типа продукта
    """


class MultipleChoiseParamsError(Exception):
    """
    Исключение множественного укзания параметров
    """


class NotFindInputError(Exception):
    """
    Исключение не найденого ID
    """


class NotCorrectInputType(Exception):
    """
    Исключение не правильных входящих параметров
    """
