class PromptingSessionNotStartedError(Exception):
	"""
		Represents a (non-exiting) exception that occurs when an requires
		that a prompting session has been started, but no session is
		currently in progress
	"""
	pass