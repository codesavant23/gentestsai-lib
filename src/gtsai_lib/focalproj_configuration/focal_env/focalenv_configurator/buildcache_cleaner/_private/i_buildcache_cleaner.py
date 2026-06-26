from abc import ABC, abstractmethod



class IBuildCacheCleaner(ABC):
	"""
		Represents an object capable of clearing the build cache for an image
		associated with the "Container Manager" to which it is bound
        
        The "Container Manager" for which it clears the cache is specified
        by the subclasses of this interface.
	"""


	@abstractmethod
	def clean_buildcache(self):
		"""
			Clears the build cache for the "Container Manager"
            specified by the subclasses of this interface
		"""
		pass