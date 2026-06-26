class IncompletePromptError(Exception):
    """
        Represents a (non-exiting) exception that occurs if you attempt to
        perform an operation that requires a full prompt, but the prompt
        used still contains placeholders
    """
    pass