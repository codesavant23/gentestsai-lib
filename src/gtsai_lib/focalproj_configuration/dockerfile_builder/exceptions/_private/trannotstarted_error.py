class TransactionNotStartedError(Exception):
	"""
		Represents a (non-exiting) exception that occurs when
		no shell command transaction has been started and
		an operation is attempted that would require one
		to be in progress.
	"""
	pass