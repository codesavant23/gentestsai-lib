class FocalProjectNotSetError(Exception):
    """
        This represents a (non-exiting) exception that occurs if you attempt to perform
        an operation in an environment configurator for focal projects without having
        previously set the data for a focal project
    """
    pass

