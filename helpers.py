def single(data, condition):
    result = []
    for element in data:
        if condition(element):
            result.append(element)
    if len(result) > 1:
        raise Exception("More than one element satisfied the condition." % msg)
    elif len(result) == 0:
        return None
    else:
        return result[0]

