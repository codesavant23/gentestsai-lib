class PromptingSessionNeverPerformedError(Exception):
	"""
		Represents a (non-exiting) exception that occurs when
		a prompting session with an LLM has never been executed
		(e.g. a sequence of correction attempts)
	"""
	pass
