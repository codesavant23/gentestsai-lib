class DefaultPythonVersionNotSetError(Exception):
	"""
		Represents a (non-exiting) exception that occurs when you perform
		an operation without first setting the desired default (fallback)
		version of Python
	"""
	pass