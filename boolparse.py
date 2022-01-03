"""Boolean parser."""

from typing import Callable, Iterator, Optional


__all__ = ['SecurityError', 'evaluate']


KEYWORDS = frozenset({' and ', ' or ', 'not ', '(', ')'})
TRUE = 'true'.casefold()


class SecurityError(Exception):
    """Indicates a possible security breach
    in parsing boolean statements.
    """


def _callback(string: str) -> bool:
    """Default callback for simple boolean evaluation."""

    return string.casefold() == TRUE


def chklim(statements: int, *, limit: Optional[int] = None) -> str:
    """Checks whether the limit has been exceeded."""

    if limit is None or statements <= limit:
        return True

    raise SecurityError('Statement limit exceeded.')


def tokenize(
        string: str, *,
        limit: Optional[int] = None,
        keywords: frozenset[str] = KEYWORDS
    ) -> Iterator[str]:
    """Tokenize the string."""

    buff = max(map(len, keywords))
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

            if lookahead in keywords:
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


def bool_val(
        statement: str,
        callback: Callable[[str], bool] = _callback
    ) -> str:
    """Evaluates the given statement into a boolean value."""

    callback_result = callback(statement)

    if isinstance(callback_result, bool):
        return str(callback_result)

    raise SecurityError('Callback method did not return a boolean value.')


def boolexpr(
        string: str, *,
        callback: Callable[[str], bool] = _callback,
        limit: Optional[int] = None,
        keywords: frozenset[str] = KEYWORDS
    ) -> Iterator[str]:
    """Yields boolean expression elements for python."""

    window = ''

    for token in tokenize(string, limit=limit, keywords=keywords):
        if not token:
            continue

        if token not in keywords:
            window += token
            continue

        if window:
            yield bool_val(window, callback)
            window = ''

        yield token

    if window:
        yield bool_val(window, callback)


def evaluate(
        string: str, *,
        callback: Callable[[str], bool] = _callback,
        limit: int = 20,
        keywords: frozenset[str] = KEYWORDS
    ) -> bool:
    """Safely evaluates a boolean string."""

    return bool(eval(''.join(boolexpr(
        string, keywords=keywords, callback=callback, limit=limit
    ))))
