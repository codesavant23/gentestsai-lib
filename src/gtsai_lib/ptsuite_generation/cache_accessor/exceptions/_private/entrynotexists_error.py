class EntryNotExistsError(Exception):
	"""
	    Represents a (non-exiting) exception that occurs if an attempt is made to access a
        production build of a partial test suite that does not exist in the
        storage space specified for the cache in question
	"""
	pass