def int_it(rawval):
    raw_result = str(rawval).replace("+", "")

    try:
        result = int(raw_result)
    except ValueError:
        result = raw_result

    return result
