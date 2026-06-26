from typing import List, Any
from ._a_base_skipwriter import _ABaseSkipWriter

# ============== JSON Utilities ============== #
from json import (
	JSONEncoder,
	JSONDecoder, JSONDecodeError
)
# ============================================ #

from ..exceptions import InvalidSkippedTestsFileError



class JsonListSkipWriter(_ABaseSkipWriter):
	"""
		This represents an `ISkipWriter` capable of writing to a JSON file.
        
        The JSON file format is as follows:
            
            [
                "skipped_entity1",
                "skipped_entity2",
                ...
            ]
	"""
	
	def __init__(
			self,
			skipdtests_path: str
	):
		"""
			Creates a new JsonListSkipWriter
            
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
		"""
		super().__init__(skipdtests_path)
		
		self._json_enc: JSONEncoder = JSONEncoder()
		self._json_dec: JSONDecoder = JSONDecoder()
		
		
	def write_skipd_test(
			self,
			entity_name: str
	):
		if entity_name == "":
			raise ValueError()
		
		content: List[str]
		with open(self._pf__get_skipdf_path(), "r") as fjson:
			content = self._json_dec.decode(fjson.read())
		
		content.append(entity_name)
		with open(self._pf__get_skipdf_path(), "w") as fjson:
			fjson.write(self._json_enc.encode(content))
			fjson.flush()
	
	
	#	============================================================
	#						PRIVATE METHODS
	#	============================================================


	def _p__file_extension(self) -> str:
		return "json"


	def _ap__init_skipdtests_file(
			self,
			skipdtests_path: str
	):
		with open(skipdtests_path, "r+") as fjson:
			fjson.write("[]")
			fjson.flush()
	
	
	def _ap__assert_skipdtests_file(
			self,
			skipdtests_path: str
	):
		content: str
		with open(self._pf__get_skipdf_path(), "r+") as fjson:
			content = fjson.read()
		
		content_obj: Any
		try:
			content_obj = self._json_dec.decode(content)
		except JSONDecodeError:
			raise InvalidSkippedTestsFileError()
		
		if not isinstance(content_obj, list):
			raise InvalidSkippedTestsFileError()