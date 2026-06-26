class PromptingSessionInProgressError(Exception):
	"""
		Represents a (non-exiting) exception that occurs when a request is made
        that no series of generation/correction attempts has been initiated,
        while, in fact, one is already in progress
	"""
	pass