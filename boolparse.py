"""Boolean parser"""

__all__ = ['SecurityError', 'BooleanEvaluator']


class SecurityError(Exception):
    """Indicates a possible security breach
    in parsing boolean statements
    """

    pass


class BooleanEvaluator():
    """Class to evaluate boolean expressions"""

    def callback(self, x):
        """Default callback for simple boolean evaluation"""
        return True if x.upper() == 'TRUE' else False

    def __init__(self, string, callback=None, limit=20, operators=None):
        """Sets the string to be parsed and optionally a
        callback method and / or an expressions limit.
        """
        self.string = string

        if callback is not None:
            self.callback = callback

        self.limit = limit
        self.operators = operators or (' and ', ' or ', 'not ', '(', ')')

    def __bool__(self):
        """Returns the string's boolean value"""
        if eval(self.cmd):
            return True
        else:
            return False

    @property
    def cmd(self):
        """Converts the string to a boolean expression in python"""
        cmdlst = []
        window = ''

        for token in self.parse():
            if token:
                if token in self.operators:
                    if window:
                        cmdlst.append(self.evaluate(window))
                        window = ''

                    cmdlst.append(token)
                else:
                    window += token

        if window:
            cmdlst.append(self.evaluate(window))

        return ' '.join(cmdlst)

    def evaluate(self, statement):
        """Evaluates the given statement into a boolean value"""
        callback_result = self.callback(statement)

        if callback_result is True or callback_result is False:
            return str(callback_result)
        else:
            raise SecurityError(
                'Callback method did not return a boolean value')

    def chklim(self, statements):
        """Checks whether the limit has not been exceeded"""
        if self.limit is None:
            return True
        elif statements > self.limit:
            raise SecurityError('Statement limit exceeded')
        else:
            return True

    def parse(self):
        """Explodes the string into a tokens
        list, considering the limit.
        """
        result = []
        window = ''
        statements = 0
        buff = max(len(op) for op in self.operators)
        skip = 0

        for pos, char in enumerate(self.string):
            if skip:
                skip -= 1
            else:
                lookahead = ''

                for offset in range(0, buff):
                    try:
                        lookahead += self.string[pos + offset]
                    except IndexError:
                        window += char
                        break
                    else:
                        if lookahead in self.operators:
                            if window:
                                statements += 1
                                self.chklim(statements)
                                result.append(window.strip())
                                window = ''

                            result.append(lookahead)
                            skip = len(lookahead) - 1
                            break
                else:
                    window += char

        # Process possibly remaining window
        if window:
            statements += 1
            self.chklim(statements)
            result.append(window.strip())

        return result
