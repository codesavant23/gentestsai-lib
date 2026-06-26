class WrongResponseFormatError(Exception):
	"""
		Represents a (non-exiting) exception that occurs when the format
		of an LLM's response does not match the format specified in the
		instructions provided in the prompt
	"""
	pass