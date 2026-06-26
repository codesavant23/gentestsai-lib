class BaseImageNotSetError(Exception):
	"""
		Represents a (non-exiting) exception that occurs when an operation
		is performed that requires a base image to be already set, but no
		base image has been set.
	"""
	pass