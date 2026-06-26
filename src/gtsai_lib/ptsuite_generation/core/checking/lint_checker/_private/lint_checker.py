from typing import Dict

from io import BytesIO
from tarfile import (
	open as tarf_open,
	TarInfo
)
# ============== Docker SDK Utilities =============== #
from docker.models.images import Image as DockerImage
# =================================================== #
# ============ Path Utilities ============ #
from os.path import (
	join as path_join,
	split as path_split,
	splitext as path_splitext,
	relpath as path_relative
)
from pathlib import PurePath
# ======================================== #
# ============== JSON Utilities ============== #
from json import JSONDecoder
# ============================================ #

from c23_logger import ATemporalFormattLogger
from c23_logger.exceptions import FormatNotSetError

from ......focalproj_configuration.focal_container import FocalContainer
from ......focalproj_configuration.focal_container.exceptions import (
	ContainerAlreadyRunningError,
	ContainerNotRunningError
)

from ..exceptions import ProjectNotSetError



class LintingChecker:
	"""
		Represents an object capable of performing linting-level validity checks on partial test suites
		using a verification tool installed within the focal environment.
		
		Public Class Attributes:
            - `LINTING_TEMP_DIR` (str) : Represents the default name of the temporary directory within the container where files used temporarily during code verification will be stored
			- `LINTING_SCRIPT` (str): Represents the default name of the Python script, located in the directory containing the linting verification tools, which will perform the verification in the focal project environment using the selected tools
	"""
	
	_RESULT_FNAME: str = "gtsai__linting_result.json"
	
	def __init__(
			self,
			path_prefix: str,
			fenv_script_fname: str,
			inputctr_dirname: str,
	        logger: ATemporalFormattLogger = None,
	):
		"""
			Creates a new LintingChecker, optionally associating it with the logger used to record
            the steps of each linting check performed.
            
            Parameters
            ----------
				path_prefix: str
                    A string containing the path prefix set for the focal environments that will
                    be used
            
                fenv_script_fname: str
                    A string containing the name of the Python script that performs the correctness check,
					at the linting level, within the focal environment
            
                inputctr_dirname: str
                    A string representing the name of the directory, within the focal environment’s path prefix,
                    that will contain the temporary copy of the partial test suites to be linted.
			
				logger: ATemporalFormattLogger
                    Optional. Default = `None`. A `ATemporalFormattLogger` object representing the logger
                    to be used to record the stages of each correction attempt (not to record the stages
                    of the request to the LLM)
					
			Raises
            ------
                ValueError
                    Occurs if:
                    
                        - The `path_prefix` parameter is `None`
                        - The `path_prefix` parameter is an empty string
						- The `fenv_script_fname` parameter is `None`
                        - The `fenv_script_fname` parameter is an empty string
                        - The `shared_dirname` parameter is `None`
                        - The `shared_dirname` parameter is an empty string
		"""
		if(path_prefix is None) or (path_prefix == ""):
			raise ValueError()
		if(fenv_script_fname is None) or (fenv_script_fname == ""):
			raise ValueError()
		if(inputctr_dirname is None) or (inputctr_dirname == ""):
			raise ValueError()
		
		self._focal_env: FocalContainer = None
		
		# Attributi relativi al progetto focale impostato
		self._proj_name: str = None
		self._full_root: str = None
		self._focal_env: FocalContainer = None
		
		# Nome dello script Python che esegue il linter all' interno dell' ambiente focale
		self._fenv_script_fname: str = fenv_script_fname
		
		# Il path prefix (o path principale) di ogni ambiente focale
		self._path_prefix: str = path_prefix
		# Nome della directory che conterrà le test-suites parziali di cui effettuare la verifica
		self._input_dir: str = inputctr_dirname
		
		# Path (reale) del risultato della verifica di linting effettuata
		self._lint_result_path: str = None
		# Path (relativa) del file con la test-suite parziale per la verifica di linting
		self._ptsuite_relpath: str = f"{self._input_dir}/temp_ptsuite.py"
		# Path (relativa) del risultato della verifica di linting effettuata da un singolo tentativo
		self._lint_result_relpath: str = None
		
		# Logger da utilizzare per loggare gli steps di ogni verifica
		self._logger: ATemporalFormattLogger = logger
		
		# Setup del formato del logger
		def_time_format: str = "( {day}-{month}-{year} | {hour}:{min}:{second} )"
		logger_frmt: str
		try:
			logger_frmt = self._logger.unset_format() if logger is not None else None
		except FormatNotSetError:
			logger_frmt = "[LintingChecker] {message} " + def_time_format
		self._logger.set_format(logger_frmt) if logger is not None else None
		
		self._inited: bool = False
		self._proj_set: bool = False
	
	
	def set_focal_project(
			self,
			project_name: str,
			full_root: str,
			env_image: DockerImage,
			path_prefix: str
	):
		"""
			Set the next focal project for which next partial test suites will require
			linting-level correctness verification.
            The focal environment associated with this project is also set containing
            linting verification tools
            
            Parameters
            ----------
				project_name: str
                    A string containing the name of the next focal project to which
                    the partial test suites requiring correctness verification belong
			
				full_root: str
                    A string containing the Full Project Root Path of the focal project to which
                    the partial test suites belong
                    
                env_image: DockerImage
                    A `docker.models.images.Image` object representing the pre-configured Docker image,
					to be used as the environment for the focal project
                    being set up
                    
                path_prefix: str
                    A string containing the path prefix used as the Full Project Root Path
                    within the provided Docker image
				
			Raises
            ------
                ValueError
                    Occurs if:
                    
                        - String parameters have a value of `None` or are empty strings
                        - The `env_image` parameter has a value of `None`
		"""
		if ((project_name is None) or (project_name == "") or
		    (full_root is None) or (full_root == "") or
			(path_prefix is None) or (path_prefix == "")
		):
			raise ValueError()
		
		# Stop dell' eventuale ambiente focale precedente
		if self._focal_env is not None:
			self._logger.log("Stop dell' ambiente focale ...") if self._logger is not None else None
			self._focal_env.stop_container()
			self._logger.log(f"Ambiente focale del progetto {self._proj_name} fermato") if self._logger is not None else None
			
			del self._focal_env
		
		self._proj_name = project_name
		self._full_root = full_root
		
		# Impostazione della path che conterrà il risultato delle verifiche di linting
		self._lint_result_path = path_join(
			self._full_root,
			"gtsai__results",
			self._RESULT_FNAME
		)
		
		# Calcolo della path relativa dei risultati (con cui si costruirà quella assoluta
		# nell' ambiente focale)
		self._lint_result_relpath = PurePath(
			path_relative(self._lint_result_path, start=self._full_root)
		).as_posix()
		
		self._focal_env = FocalContainer(
			env_image,
			self._full_root,
			path_prefix,
		)
		
		if not self._proj_set:
			self._proj_set = True
		
		# Avvio dell' ambiente focale (container)
		self._logger.log("Launching the focal environment ...") if self._logger is not None else None
		self._focal_env.start_container()
		
		# Creazione della directory temporanea
		self._create_inputctr()

		self._logger.log(f"Focal environment of the project '{self._proj_name}' launched!") if self._logger is not None else None


	def check_lintically(
			self,
			ptsuite_code: str
	) -> Dict[str, str]:
		"""
			Performs a syntax check on the partial test suite provided as an argument
            
            Parameters
            ----------
				ptsuite_code: str
                    A string containing the code of the partial test suite to be
                    checked for syntactic correctness
                    
            Returns
            -------
				Dict[str, str]
                    A dictionary of strings, indexed by strings representing the first error highlighted
                    by the linting check performed. Optionally contains:
                        
                        - "except_name": The name of the issue found during the linting check
						- "except_mess": The message associated with the issue found during the linting check
                        - "except_pos": The line and column numbers (separated by ";") where the issue was found

                    If no errors were found, an empty dictionary is returned
					
			Raises
            ------
                ValueError
                    Occurs if the `ptsuite_code` parameter is `None` or an empty string
                    
                ProjectNotSetError
                    Occurs if:
						
						- A focal project has never been set
                        - You must set a focal project before running this operation again
                    
                OSError
                    If problems occur when opening or writing to the temporary file used
                    for verification
		"""
		if (ptsuite_code is None) or (ptsuite_code == ""):
			raise ValueError()
		if not self._proj_set:
			raise ProjectNotSetError()
		if not self._inited:
			self._create_inputctr()
			
		self._logger.log(
			f"Starting the linting check ..."
		) if self._logger is not None else None
		
		self._logger.log("Writing the partial test suite in the focal environment ...") if self._logger is not None else None
		tarfile_stream: BytesIO = BytesIO()
		ptsuite_code_b: bytes = ptsuite_code.encode("utf-8")
		with tarf_open(fileobj=tarfile_stream, mode="w") as tfptsuite:
			tarfile_info: TarInfo = TarInfo(name=path_split(self._ptsuite_relpath)[1])
			tarfile_info.size = len(ptsuite_code_b)
			tfptsuite.addfile(tarinfo=tarfile_info, fileobj=BytesIO(ptsuite_code_b))
		tarfile_stream.seek(0)
		self._focal_env.put_tararchive(
			f"{self._path_prefix}/{self._input_dir}",
			tarfile_stream
		)
		self._logger.log("Partial test suite written!") if self._logger is not None else None
		
		# Richiesta della verifica della correttezza (a livello di linting)
		self._logger.log("Running linting check ...") if self._logger is not None else None
		self._focal_env.execute(
			f"/bin/bash -c 'python -m $LINTTOOLS_DIRNAME.{path_splitext(self._fenv_script_fname)[0]} "
			f"{self._ptsuite_relpath} {self._lint_result_relpath}'"
		)
		self._logger.log("Linting check completed!") if self._logger is not None else None
		
		# Lettura del risultato della verifica di correttezza
		self._logger.log("Reading the test results ...") if self._logger is not None else None
		json_dec: JSONDecoder = JSONDecoder()
		result: Dict[str, str] = None
		with open(self._lint_result_path, "r") as fjson:
			result = json_dec.decode(fjson.read())
		self._logger.log("Test results acquired!") if self._logger is not None else None
		
		self._logger.log("End of the linting check") if self._logger is not None else None
		return result
	
	
	def clear_resources(self, stop_fenv: bool=False):
		"""
			Cleans up resources used by the verifier during linting
            
            Parameters
            ----------
				stop_fenv: bool
                    Optional. Default = `False`. A boolean indicating whether to stop the instance
                    of the focal environment that was started when the focal project was set
		"""
		if stop_fenv and (self._focal_env is not None):
			self._logger.log("Shutting down focal environment ...") if self._logger is not None else None
			self._focal_env.stop_container()
			self._logger.log(f"Focal environment of the project '{self._proj_name}' shut down") if self._logger is not None else None
			self._proj_set = False
			
			del self._focal_env
			self._focal_env = None

		self._inited = False
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================


	def _create_inputctr(self):
		"""
			Create a temporary directory, within the focal environment, for the files
			required to run the linting check
		"""
		if not self._proj_set:
			raise ProjectNotSetError()
		
		try:
			self._focal_env.start_container()
			self._focal_env.stop_container()
			raise ContainerNotRunningError()
		except ContainerAlreadyRunningError:
			pass
		
		self._focal_env.execute(f"mkdir -p {self._path_prefix}/{self._input_dir}")
		
		self._inited = True