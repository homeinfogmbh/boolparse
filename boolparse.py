"""Boolean parser."""

from typing import Callable, Iterator


__all__ = ['SecurityError', 'evaluate']


PARENTHESES = frozenset({'(', ')'})
KEYWORDS = frozenset({'and', 'or', 'not'})


class SecurityError(Exception):
    """Indicates a possible security breach
    in parsing boolean statements.
    """


def bool_val(token: str, callback: Callable[[str], bool]) -> str:
    """Evaluates the given statement into a boolean value."""

    callback_result = callback(token)

    if isinstance(callback_result, bool):
        return str(callback_result)

    raise SecurityError('Callback method did not return a boolean value.')


def tokenize(word: str) -> Iterator[str]:
    """Yields tokens of a string."""

    for index, char in enumerate(word):
        if char in PARENTHESES:
            yield word[:index]
            yield char
            yield from tokenize(word[index+1:])
            break
    else:
        yield word


def boolexpr(string: str, callback: Callable[[str], bool]) -> Iterator[str]:
    """Yields boolean expression elements for python."""

    for word in string.strip().split():
        for token in filter(None, tokenize(word)):
            if token in KEYWORDS or token in PARENTHESES:
                yield token
            else:
                yield bool_val(token, callback)


def evaluate(
        string: str, *,
        callback: Callable[[str], bool] = lambda s: s.casefold() == 'true'
    ) -> bool:
    """Safely evaluates a boolean string."""

    return bool(eval(' '.join(boolexpr(string, callback))))
