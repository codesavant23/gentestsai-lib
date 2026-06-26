class ContainerNotRunningError(Exception):
	"""
        Represents a (non-exiting) exception that occurs when an operation is
        performed that requires a Docker container, associated with a focal
        project, to be running
    """
	pass
