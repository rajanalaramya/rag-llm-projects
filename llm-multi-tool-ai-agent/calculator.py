def calculator(expression):
    allowed_chars = "0123456789+-*/(). """
    for char in expression:
        if char not in expression:
            raise ValueError(f"Invalid character '{char}' in expression.")
    result = eval(expression)
    return result