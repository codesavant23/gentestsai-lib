from abc import ABC, abstractmethod



class ISkipWriter(ABC):
	"""
		Represents a writer of files containing skipped tests during the generation or correction
		phase by an LLM.
        
        The file type of the skipped tests is specified by the descendants of this interface.
        The file format of the skipped tests is specified by the descendants of this interface.
	"""


	@abstractmethod
	def write_skipd_test(
			self,
			entity_name: str
	):
		"""
			Writes to the associated file that the attempt to generate, via LLM, a partial test suite,
			linked to the specified entity, was unsuccessful.
            
            The file is always flushed at the end of this operation
			
			Parameters
            ----------
                entity_name: str
                    A string containing the fully-qualified name of the autonomous code entity
                    whose generation or correction was unsuccessful
					
			Raises
            ------
                ValueError
                    Occurs if the given string is empty
                    
                OSError
                    Occurs if writing to the associated file is not possible
		"""
		pass