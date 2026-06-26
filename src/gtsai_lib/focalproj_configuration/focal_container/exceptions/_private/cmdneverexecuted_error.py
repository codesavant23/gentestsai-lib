class CommandNeverExecutedError(Exception):
	"""
		Represents a (non-exiting) exception that occurs when an
		operation is performed that requires a shell command to have
		already been executed
	"""
	pass