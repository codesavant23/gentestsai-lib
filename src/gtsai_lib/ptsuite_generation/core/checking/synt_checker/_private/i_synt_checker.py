from typing import Tuple
from abc import ABC, abstractmethod



class ISyntacticChecker(ABC):
	"""
		Represents an object capable of verifying the syntactic correctness of a partial test suite
		using a verification tool.
    
        The verification tool is specified by the descendants of this interface.
	"""


	@abstractmethod
	def check_synt(
			self,
			ptsuite_code: str
	) -> Tuple[str, str]:
		"""
			Performs a syntax check on the partial test suite provided as an argument
            
            Parameters
            ----------
                ptsuite_code: str
					A string containing the code of the partial test suite for which to perform the syntax check
            
            Returns
            -------
                Tuple[str, str]
                    A tuple of two strings representing the first error, if any, found
					by the syntax check performed. It optionally contains:
                        
                        - [0]: The name of the issue found during the syntax check
                        - [1]: The message associated with the issue found during the syntax check

					If no errors were found, an empty tuple is returned
            
            Raises
            ------
                ValueError
                    Occurs if the `ptsuite_code` parameter is `None` or an empty string
                    
                SyntacticCheckError
                    Occurs if the syntax checking process cannot be completed.
                    This includes failures caused by the underlying checker,
                    external tool execution, or required source preparation.
		"""
		pass
	
	
	@abstractmethod
	def clear_resources(self):
		"""
			Clears the resources that were used by the syntactic checker
		"""
		pass