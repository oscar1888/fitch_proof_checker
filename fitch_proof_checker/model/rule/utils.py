def flatten_connective(formula, connective_class) -> list:
    res = []
    stack = [formula]

    while stack:
        current = stack.pop()
        if type(current) is connective_class:
            stack.extend(reversed(current.args))
        else:
            res.append(current)

    return res
