from typing import Tuple
from ._a_base_syntcker import _ABaseSyntacticChecker

from datetime import datetime as DateTime
from py_compile import (
	compile as py_compile,
	PycInvalidationMode as Pyc_InvMode,
	PyCompileError
)
# ============ Path Utilities ============ #
from os.path import join as path_join
# ======================================== #
# ============== OS Utilities ============== #
from os import makedirs as os_mkdirs
from shutil import rmtree as os_dremove
from tempfile import gettempdir as os_tempdir
# ========================================== #
# ============= RegEx Utilities ============ #
from regex import search as reg_search
# ========================================== #

from ..exceptions import SourceMaterializationError



class PyCompileSyntChecker(_ABaseSyntacticChecker):
	"""
		Represents an `ISyntChecker` that uses the verification tool
        `pycompile`.
	"""
	
	_PYCOMP_EXCNAME_PATT: str = r"[A-Z][\w_\-]+Error"
	
	def __init__(self):
		"""
			Creates a new PyCompileSyntChecker
		"""
		timestamp: str = str(int(DateTime.now().timestamp() * 1000))
		temp_fname: str = f"temp_{timestamp}.py"
		self._TEMP_BASEPATH: str = path_join(
			os_tempdir(),
			"gentests_ai",
			"correction",
			"synt"
		)
		
		os_dremove(self._TEMP_BASEPATH, ignore_errors=True)
		os_mkdirs(self._TEMP_BASEPATH)
		self._inited: bool = True
		
		self._tempfile_path: str = path_join(
			self._TEMP_BASEPATH,
			temp_fname
		)
		
		
	def _ap__check_synt_spec(self, ptsuite_code: str) -> Tuple[str, str]:
		try:
			self._write_on_tempfile(ptsuite_code)
		except OSError:
			raise SourceMaterializationError()
		
		try:
			py_compile(
				self._tempfile_path,
				doraise=True,
				invalidation_mode=Pyc_InvMode.TIMESTAMP
			)
			return tuple()
		except PyCompileError as synt_error:
			except_name: str = reg_search(
				self._PYCOMP_EXCNAME_PATT,
				synt_error.exc_type_name
			).group()
			except_mess: str = synt_error.args[0]
			return (except_name, except_mess)
	
	
	def clear_resources(self):
		os_dremove(self._TEMP_BASEPATH, ignore_errors=True)
		self._inited = False
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================


	def _write_on_tempfile(self, ptsuite_code: str):
		"""
			Writes the partial test suite to the temporary file
            for syntax checking
            
            Parameters
            ----------
				ptsuite_code: str
                    A string containing the code of the partial test suite for which
                    syntax correctness verification is to be performed
                    
            Raises
            ------
                OSError
                    Occurs if there are any problems with writing on the temporary file
		"""
		if not self._inited:
			os_dremove(self._TEMP_BASEPATH, ignore_errors=True)
			os_mkdirs(self._TEMP_BASEPATH)
			self._inited = True
		
		with open(self._tempfile_path, "w") as fptsuite:
			fptsuite.write(ptsuite_code)
			fptsuite.flush()