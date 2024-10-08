class ErrorTypeProductStripe(Exception):
    """
    Исключение не правильного типа продукта
    """


class MultipleChoiseParamsError(Exception):
    """
    Исключение множественного укзания параметров
    """


class DoNotFindIDProductError(Exception):
    """
    Исключение не найденого ID
    """
