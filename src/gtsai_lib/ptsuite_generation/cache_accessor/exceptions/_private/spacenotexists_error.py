class ProjectSpaceNotExistsError(Exception):
	"""
	    Represents a (non-exiting) exception that occurs if you attempt to access a
        storage space of a focal project that does not exist in the cache in question
	"""
	pass