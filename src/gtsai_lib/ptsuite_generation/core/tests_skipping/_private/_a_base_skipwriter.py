from abc import abstractmethod
from .. import ISkipWriter

# ============ Path Utilities ============ #
from os.path import splitext as path_splitext
# ======================================== #
# ============== OS Utilities ============== #
from os.path import exists as os_fdexists
# ========================================== #

from ..exceptions import InvalidSkippedTestsFileError



class _ABaseSkipWriter(ISkipWriter):
	"""
		Represents a base `ISkipWriter` that contains the logic common to all `ISkipWriter`s.
        
        The file type for skipped tests is specified by the descendants of this abstract class.
        The file format for skipped tests is specified by the descendants of this abstract class.
	"""
	
	def __init__(
			self,
			skipdtests_path: str
	):
		"""
			Creates a new _ABaseSkipWriter and associates it with the path
            that contains, or will contain, the skipped tests file
            
            Parameters
            ----------
				skipdtests_path: str
                    A string representing the path that contains, or will contain,
                    the file of skipped tests to be used
                    
            Raises
            ------
                ValueError
                    Occurs if:
						
						- The `skipdtests_path` parameter is `None`
                        - The `skipdtests_path` parameter is an empty string

                InvalidSkippedTestsFileError
                    Occurs if the file is invalid in terms of type or format
		"""
		if (skipdtests_path is None) or (skipdtests_path == ""):
			raise ValueError()
		
		self._skipd_path: str = skipdtests_path
		
		
	def _p__file_extension(self) -> str:
		"""
			Returns the extension required for the file containing the skipped tests.
            
            Implementing this method is optional if the file type does not require
            a specific extension.
            
            Returns
            -------
				str
                    A string, in lowercase and without a period, containing the extension
                    that the skipped tests file must have.
		"""
		return ""
		
		
	def _pf__get_skipdf_path(self) -> str:
		"""
			Returns the path containing the file of skipped tests
            
            Returns
            -------
                str
                    A string representing the path containing the file of skipped tests to be used
		"""
		return self._skipd_path
	
	
	def _P__objinit(self):
		"""
			Verifies/ensures the invariants of the newly constructed object
			
			Raises:
            ------
                InvalidSkippedTestsFileError
                    Occurs if the path does not represent a skipped tests file of a type or format
                    compatible with those specified by the descendants of this abstract class,
                    in case the file already exists.
		"""
		extens: str = self._p__file_extension()
		if extens != "":
			if path_splitext(self._skipd_path)[1].lower() != f".{extens}":
				raise InvalidSkippedTestsFileError()
			
		if os_fdexists(self._skipd_path):
			self._ap__assert_skipdtests_file(self._skipd_path)
		else:
			open(self._skipd_path, "w").close()
			self._ap__init_skipdtests_file(self._skipd_path)
		
		
	#	============================================================
	#						ABSTRACT METHODS
	#	============================================================
	
	
	@abstractmethod
	def _ap__assert_skipdtests_file(
			self,
			skipdtests_path: str
	):
		"""
			Check that the skipped-tests file, located at the specified path, is valid
            according to the type and format specified by the descendants of this abstract class.

			If the skipped-tests file is valid, this operation is equivalent to a no-op.
			
			The following are guaranteed within this method:
                
                - That the `skipdtests_path` parameter is not `None`
                - That the `skipdtests_path` parameter is not an empty string
				- That the file at the path `skipdtests_path` exists
                - That the `skipdtests_path` parameter points to a file with the correct extension
            
            Parameters
            ----------
				skipdtests_path: str
                    A string representing the path to the file containing the skipped tests
                    to be used
                    
            Raises
            ------
                InvalidSkippedTestsFileError
                    Occurs if the file is invalid in terms of type or format
		"""
		pass
	
	
	@abstractmethod
	def _ap__init_skipdtests_file(
			self,
			skipdtests_path: str
	):
		"""
			Initializes the skipped-tests file based on the file format specified by the subclasses of this abstract class.
            
            If the skipped-tests file is valid, this operation is equivalent to a no-op.
			
			The following are guaranteed within this method:
                
                - That the `skipdtests_path` parameter is not `None`
                - That the `skipdtests_path` parameter is not an empty string
                - That the file at the `skipdtests_path` is empty
			
			Parameters
            ----------
                skipdtests_path: str
                    A string representing the path containing the file of skipped tests
                    to be used
		"""
		pass
	
	
	@abstractmethod
	def write_skipd_test(self, entity_name: str):
		pass