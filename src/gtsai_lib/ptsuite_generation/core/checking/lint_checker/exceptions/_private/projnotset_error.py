class ProjectNotSetError(Exception):
	"""
		Represents a (non-exiting) exception that occurs when a focal project has not been
        set in the linting checker in question before performing a specific operation
	"""
	pass