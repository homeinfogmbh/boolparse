"""Boolean parser."""

__all__ = ['SecurityError', 'evaluate']


OPERATORS = (' and ', ' or ', 'not ', '(', ')')


class SecurityError(Exception):
    """Indicates a possible security breach
    in parsing boolean statements.
    """

    pass


def _callback(string):
    """Default callback for simple boolean evaluation."""

    return string.upper() == 'TRUE'


def chklim(statements, limit=None):
    """Checks whether the limit has been exceeded."""

    if limit is None or statements <= limit:
        return True

    raise SecurityError('Statement limit exceeded.')


def tokenize(string, limit=None, operators=OPERATORS):
    """Tokenize the string."""

    buff = max(len(operator) for operator in operators)
    window = ''
    statements = 0
    skip = 0

    for pos, char in enumerate(string):
        if skip:
            skip -= 1
            continue

        lookahead = ''

        for offset in range(buff):
            try:
                lookahead += string[pos + offset]
            except IndexError:
                window += char
                break

            if lookahead in operators:
                if window:
                    statements += 1
                    chklim(statements, limit=limit)
                    yield window.strip()
                    window = ''

                yield lookahead
                skip = len(lookahead) - 1
                break
        else:
            window += char

    # Process possibly remaining window
    if window:
        statements += 1
        chklim(statements, limit=limit)
        yield window.strip()


def bool_val(statement, callback=_callback):
    """Evaluates the given statement into a boolean value."""

    callback_result = callback(statement)

    if isinstance(callback_result, bool):
        return str(callback_result)

    raise SecurityError('Callback method did not return a boolean value.')


def boolexpr(string, callback=_callback, limit=None, operators=OPERATORS):
    """Yields boolean expression elements for python."""

    window = ''

    for token in tokenize(string, limit=limit, operators=operators):
        if token:
            if token in operators:
                if window:
                    yield bool_val(window, callback)
                    window = ''

                yield token
            else:
                window += token

    if window:
        yield bool_val(window, callback)


def evaluate(string, callback=_callback, limit=20, operators=OPERATORS):
    """Safely evaluates a boolean string."""

    command = ' '.join(boolexpr(
        string, operators=operators, callback=callback, limit=limit))

    return bool(eval(command))
