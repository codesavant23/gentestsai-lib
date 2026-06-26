class InvalidPlaceholderError(Exception):
    """
        Represents a (non-exiting) exception that occurs if you attempt
        to use a placeholder that cannot be used in a prompt template
    """
    pass