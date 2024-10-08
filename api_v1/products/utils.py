def add_params(target: dict,
               **params,
               ) -> dict:
    """
    Добавляет доп параметры в словарь
    """
    target = target.copy()
    updated_dict = target | params
    return updated_dict
