class SyntacticallyIncorrectPtsuiteError(Exception):
    """
        Represents an exception (non-exiting) that occurs if an operation expects
        a syntactically correct partial test suite but is provided with one that is
        syntactically incorrect
    """
    pass

