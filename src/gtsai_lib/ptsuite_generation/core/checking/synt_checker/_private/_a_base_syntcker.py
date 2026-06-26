from typing import Tuple
from abc import abstractmethod
from .. import ISyntacticChecker



class _ABaseSyntacticChecker(ISyntacticChecker):
	"""
		Represents a basic `ISyntacticChecker`, containing the logic common
		to all `ISyntacticChecker`s.
        
        The verification tool is specified by the descendants of this interface.
	"""
	
	
	def check_synt(
			self,
			ptsuite_code: str
	) -> Tuple[str, str]:
		if (ptsuite_code is None) or (ptsuite_code == ""):
			raise ValueError()
			
		return self._ap__check_synt_spec(ptsuite_code)
		
	
	##	============================================================
	##						ABSTRACT METHODS
	##	============================================================
	
	
	@abstractmethod
	def _ap__check_synt_spec(self, ptsuite_code: str) -> Tuple[str, str]:
		"""
			Performs a syntax check on the partial test suite provided as an argument
			using the verification tool specified by the descendants of this abstract class.
            
            This method guarantees that the `ptsuite_code` parameter is neither
			the value `None` nor it's an empty string.
            
            Parameters
            ----------
                ptsuite_code: str
                    A string containing the code of the partial test suite for which
                    to perform the syntax check
			
			Returns
			-------
                Tuple[str, str]
                    A tuple of 2 strings representing the first syntax error, if any,
                    in the partial test suite. It optionally contains:
					
						- [0]: The name of the issue found during the correctness check
                        - [1]: The message associated with the issue found during the correctness check
                        
                    If no errors occurred, an empty tuple is returned
                    
            Raises
            ------
                SyntacticCheckError
                    Occurs if the syntax checking process cannot be completed.
                    This includes failures caused by the underlying checker,
                    external tool execution, or required source preparation.
		"""
		pass


	@abstractmethod
	def clear_resources(self):
		pass


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================