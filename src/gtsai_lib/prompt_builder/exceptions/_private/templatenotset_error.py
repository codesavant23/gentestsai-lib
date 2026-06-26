class TemplateNotSetError(Exception):
	"""
		Represents a (non-exiting) exception that occurs when an operation is executed
        without having set a prompt template beforehand
	"""
	pass