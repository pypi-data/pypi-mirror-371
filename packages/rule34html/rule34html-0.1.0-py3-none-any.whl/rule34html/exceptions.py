class Rule34Error(Exception):
    """Base error for rule34html."""

class NotFound(Rule34Error):
    pass

class ParseError(Rule34Error):
    pass
