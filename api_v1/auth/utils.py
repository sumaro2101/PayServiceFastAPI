def int_to_base36(i):
    """Convert an integer to a base36 string."""
    char_set = "0123456789abcdefghijklmnopqrstuvwxyz"
    if i < 0:
        raise ValueError("Negative base36 conversion input.")
    if i < 36:
        return char_set[i]
    b36 = ""
    while i != 0:
        i, n = divmod(i, 36)
        b36 = char_set[n] + b36
    return b36


def base36_to_int(s):
    """
    Convert a base 36 string to an int. Raise ValueError if the input won't fit
    into an int.
    """
    if len(s) > 13:
        raise ValueError("Base36 input too large")
    return int(s, 36)
