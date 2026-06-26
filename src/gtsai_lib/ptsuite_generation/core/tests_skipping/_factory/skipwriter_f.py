from .. import ISkipWriter
from .e_skipdtests_filetype import ESkippedTestsFtypeFormat

from .._private._a_base_skipwriter import _ABaseSkipWriter
from .._private.jsonlist_skipwriter import JsonListSkipWriter



class SkipWriterFactory:
	"""
		Represents a factory for each `ISkipWriter`
	"""
	
	
	@classmethod
	def create(
			cls,
			file_type: ESkippedTestsFtypeFormat, 
			skipdtests_path: str
	) -> ISkipWriter:
		"""
			Instantiates a new skipped tests file writer of the specified type and format
            
            Parameters
            ----------
                file_type: ESkippedTestsFtypeFormat
                    An `ESkippedTestsFtypeFormat` value representing the required type and format
					of the files that the `ISkipWriter` object is capable of writing
                
                skipdtests_path: str
                    A string representing the path that contains, or will contain,
                    the file of skipped tests to be used
                    
            Returns
            -------
				ISkipWriter
                    An `ISkipWriter` object that allows skipped tests to be written
                    in the specified type and format
                    
            Raises
            ------
                ValueError
                    Occurs if:
						
						- The `skipdtests_path` parameter is `None`
                        - The `skipdtests_path` parameter is an empty string
            
                InvalidSkippedTestsFileError
                    Occurs if the file is invalid in terms of type or format
		"""
		obj: _ABaseSkipWriter
		match file_type:
			case ESkippedTestsFtypeFormat.JSON:
				obj = JsonListSkipWriter(skipdtests_path)
		
		obj._P__objinit()
		return obj
	
		
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================