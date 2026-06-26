class TransactionStartedError(Exception):
	"""
		This is a (non-exiting) exception that occurs when a shell command
		transaction is in progress and you attempt to perform an operation
		that should not be performed while a transaction is in progress.
	"""
	pass