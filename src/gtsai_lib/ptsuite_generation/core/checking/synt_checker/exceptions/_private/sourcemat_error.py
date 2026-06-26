from .syntcheck_error import SyntacticCheckError



class SourceMaterializationError(SyntacticCheckError):
    """
        Represents an exception (non-exiting) that occurs when
        source code cannot be materialized for perform syntax checking.
    """
    pass