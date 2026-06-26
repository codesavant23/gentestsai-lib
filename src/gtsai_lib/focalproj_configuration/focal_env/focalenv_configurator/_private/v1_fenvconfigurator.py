from typing import Tuple
from ._a_base_fenvconfigurator import _ABaseFocalEnvConfigurator

from ..buildcache_cleaner import EContainerManager



class V1FocalEnvConfigurator(_ABaseFocalEnvConfigurator):
	"""
		Represents an `IFocalEnvConfigurator` that creates focal environment images
        with `pylint=="3.2.3"` and `coverage.py=="7.2.3"` installed
	"""
	
	def __init__(
			self,
			image_prefix: str,
			gentests_dir: str,
			envconfig_dir: str,
			dockerfile_fname: str,
			py_vers_fname: str,
			deps_files: Tuple[str, str, str, str, str, str],
			tools_root: str,
			linttools_dir: str,
			covtools_dir: str,
			path_prefix: str = None,
			pref_contman: EContainerManager = None,
	):
		"""
			It creates a new V1FocalEnvConfigurator and associates it with:
                
                - The `ATransactDockfBuilder` to be used to build the image's Dockerfile
                - The Env-Config Project Root Path structure
                - The name assigned to the Gen-tests Project Root Path directory
				
			After that, you must execute:
            
                - The `.set_focal_project(...)` operation
                - The `.set_default_pyversion(...)` operation
                
            Parameters
            ----------
				image_prefix: str
                    A string containing the prefix to be appended to the tag of each image
                    that will be built
                    
                gentests_dir: str
                    A string containing the name of the directory containing the tests generated
                    by the LLMs
					
				envconfig_dir: str
                    A string containing the name of the Env-Config Project Root Path directory
                    for each focal project
                
                dockerfile_fname: str
					A string containing the name of the Dockerfile that will be generated for each image of the target environment
                
                py_vers_fname: str
                    A string representing the name of any file containing the specific tag of the "python" image to be used in place of the fallback image

				deps_files: Tuple[str, str, str, str, str, str]
                    A 6-tuple of strings containing:
                        
                        - [0]: The name of the file (if any) specifying the Python dependencies of the target project
                        - [1]: The name of any file specifying the non-Python dependencies of the target project
                        - [2]: The name of any script containing the shell code to be executed before installing external dependencies
                        - [3]: The name of any script containing the shell code to be executed after installing external dependencies
						- [4]: The name of any script containing the shell code to be executed before installing Python dependencies
                        - [5]: The name of any script containing the shell code to be executed after installing Python dependencies
            
                tools_root: str
					A string representing the path containing the tools to be used within the target environment
                
                
                linttools_dir: str
                    A string containing the name of the directory, within `tools_root`,
                    that contains the tools for performing linting checks
					
				covtools_dir: str
                    A string containing the name of the directory, within `tools_root`,
                    that contains the tools for calculating code coverage
					
				path_prefix: str
                    Optional. Default = `None`. A string representing the initial path prefix (if any)
                    to be used for images produced with this IFocalEnvConfigurator
                    
                pref_contman: EContainerManager
					Optional. Default = `None`. An `EContainerManager` value indicating the container manager to be used for managing focal environments.
                    If `None` is provided (or no value is provided), the primary container manager installed on the operating system is considered selected. (See "Container Manager Selection Criteria"
					in the full documentation)
            
            Raises
            ------
                ValueError
                    Occurs if:
                    
                        - The `gentests_dir` parameter is `None` or an empty string
						- The `envconfig_dir` parameter is `None` or an empty string
                        - The `dockerfile_fname` parameter is `None` or an empty string
                        - The `py_vers_fname` parameter is `None` or an empty string
						- The `deps_files` parameter is `None`, is an empty tuple; or one of its elements is `None` or at least one is an empty string
                        - The `tools_root` parameter is `None`, is an empty string, or is an invalid path
						- The `linttools_dir` parameter is `None`, an empty string, or the directory does not exist in `tools_root`
                        - The `path_prefix` parameter is an empty string or an invalid Linux path
		"""
		super().__init__(
			image_prefix,
			gentests_dir, envconfig_dir,
			dockerfile_fname,
			py_vers_fname,
			deps_files,
			tools_root, linttools_dir, covtools_dir,
			path_prefix, pref_contman
		)
	
	
	def _ap__pylint_version(self) -> str:
		return "3.2.3"
	
	
	def _ap__covpy_version(self) -> str:
		return "7.2.3"
	

	##	============================================================
	##						PRIVATE METHODS
	##	============================================================