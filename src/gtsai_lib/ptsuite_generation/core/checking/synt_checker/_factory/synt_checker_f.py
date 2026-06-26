from .. import ISyntacticChecker

from .e_synt_chker_tool import ESyntCheckerTool
from .._private.pycomp_syntcker import PyCompileSyntChecker



class SyntacticCheckerFactory:
	"""
		Represents a factory for each `ISyntacticChecker`
	"""
	
	
	@classmethod
	def create(
			cls,
			tool: ESyntCheckerTool,
	) -> ISyntacticChecker:
		"""
			Instantiates a new syntactic checker that uses the specified
			verification tool
            
            Parameters
            ----------
				tool: ESyntCheckerTool
                    An `ESyntCheckerTool` value representing the verification tool that
                    the `ISyntacticChecker` object must use
                    
            Returns
            -------
				ISyntacticChecker
                    An `ISyntacticChecker` object that allows for the verification of
                    syntactic correctness of a partial test suite using the specified
                    verification tool
		"""
		obj: ISyntacticChecker
		match tool:
			case ESyntCheckerTool.PYCOMPILE:
				obj = PyCompileSyntChecker()
			
		return obj
		
		
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================