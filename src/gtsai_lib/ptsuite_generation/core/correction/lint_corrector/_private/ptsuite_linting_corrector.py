from typing import Tuple

from datetime import datetime as DateTime
# ============== OS Utilities ============== #
from os import (
	makedirs as os_mkdirs,
	remove as os_remove,
)
from os.path import exists as os_fdexists
from tempfile import gettempdir as os_tempdir
# ========================================== #
# ============ Path Utilities ============ #
from os.path import join as path_join
# ======================================== #
# ============= RegEx Utilities ============ #
from regex import (
	search as reg_search,
	Match,
	RegexFlag as RegexFlags
)
# ========================================== #
from py_compile import (
	compile as py_compile,
	PycInvalidationMode as Pyc_InvMode,
	PyCompileError
)

from ....checking.lint_checker import LintingChecker

from llm_access.llm_apiaccessor import ILlmApiAccessor
from llm_access.llm_apiaccessor.exceptions import (
	ApiResponseError,
	SaturatedContextWindowError,
	ResponseTimedOutError
)

from c23_logger import ATemporalFormattLogger
from c23_logger.exceptions import FormatNotSetError

from ....exceptions import (
	PromptingSessionNeverPerformedError,
	PromptingSessionNotStartedError,
	PromptingSessionInProgressError,
	WrongResponseFormatError
)
from ..exceptions import SyntacticallyIncorrectPtsuiteError



class PtsuiteLintingCorrector:
	"""
		Represents an object capable of performing correction attempts
		on partial test suites, after verifying the correctness of their code
		at the linting level.
        
        Public Class Attributes:
            - `GENCODE_PATT` (str) : Represents the default regex pattern to be used to identify the code in the response of a correction attempt
	"""
	
	GENCODE_PATT: str = r"```python\n?(?P<gen_code>[\s\S]+)\n?```"
	
	def __init__(
			self,
			max_tries: int,
			llm_accsor: ILlmApiAccessor,
			lint_checker: LintingChecker,
			resp_format: str = None,
			logger: ATemporalFormattLogger = None,
	):
		"""
			Creates a new PtsuiteLintingCorrector and associates it with an `ILlmApiAccessor`
            which will be used to send correction requests to the LLMs that will be, or have been,
            configured.
			
			It may also be associated with the logger used to record the stages of each
            generation attempt, and with a response format different from the default
            (default format: `self.GENCODE_PATT`)

            Parameters
            ----------
				max_tries: int
                    An integer indicating the maximum number of attempts to make
                    in requests
            
                llm_accsor: ILlmApiAccessor
                    An `ILlmApiAccessor` object that will be used to make correction requests
					
				lint_checker: str
                    An `LintingChecker` object representing the linting checker to be used
                    to test the correctness of the partial test suite after each attempt
					
				resp_format: str
                    Optional. Default = `None`. A RegEx string containing the format to use to identify
                    the code resulting from the correction attempts made.
                    It must contain a named group called "gen_code"
					
				logger: ATemporalFormattLogger
                    Optional. Default = `None`. An `ATemporalFormattLogger` object representing the logger
                    to be used to record the stages of each correction attempt (not to record the stages
                    of the request to the LLM)
					
			Raises:
            ------
                ValueError
                    Occurs if:
					
						- The `max_tries` parameter is less than 1
                        - The `llm_accsor` parameter is `None`
                        - The `lint_checker` parameter is `None`
                        - The `response_format` parameter is provided but does not contain a named group called "gen_code"
		"""
		if max_tries < 1:
			raise ValueError()
		
		self._resp_regex: str =	self.GENCODE_PATT
		if resp_format is not None:
			if resp_format.find("(?P<gen_code>") == -1:
				raise ValueError()
			self._resp_regex = resp_format
		
		# Attributi per la gestione della serie di correzioni
		self._corr_everperf: bool = False
		self._corr_inprogr: bool = False
		self._max_tries: int = max_tries
		self._times_tried: int = 0
		self._try_succ: bool = False
		self._resp_tout: int = 0
		
		# Attributi riguardanti ogni tentativo di correzione
		self._last_corrpts: str = ""
		self._max_tries: int = max_tries
		self._llm_platf: ILlmApiAccessor = llm_accsor
		
		# Verificatore di linting delle test-suite parziali
		self._lint_chker: LintingChecker = lint_checker
		
		# Logger da utilizzare per loggare gli steps di ogni tentativo
		self._logger: ATemporalFormattLogger = logger
		
		
	def has_corr_terminated(self) -> bool:
		"""
			Checks whether the current attempts sequence has ended, either because 
			the correction was successful or because the maximum number of attempts 
			has been reached 
            
            Returns
            -------
                bool
					A boolean indicating whether the previously started attempts
					sequence has ended
					
			Raises
			------
                PromptingSessionNeverPerformedError
                    Occurs if an attempts sequence has never been started
		"""
		if not self._corr_everperf:
			raise PromptingSessionNeverPerformedError()
		
		return not self._corr_inprogr


	def has_corr_succ(self) -> bool:
		"""
			Checks whether the last generation attempt was successful
            generating a partial test suite

            Returns
            -------
				bool
                    A boolean indicating whether the last partial test suite that
                    was attempted to be generated was successful

			Raises
            ------
                PromptingSessionNeverPerformedError
                    Occurs if no sequence of attempts has ever been performed
            
                PromptingSessionInProgressError
                    Occurs if a sequence of correction attempts is currently in progress
		"""
		if not self._corr_everperf:
			raise PromptingSessionNeverPerformedError()
		if self._corr_inprogr:
			raise PromptingSessionInProgressError()
		
		return self._try_succ
	
	
	def get_lastcorr(self) -> Tuple[str, int]:
		"""
			Returns a tuple containing:
			
                - The code resulting from the last attempt to fix a partial test suite
                - The attempt number at which the fix was successful

            To verify the success of the last sequence of attempts, you must use
            the `.has_corr_succ(...)` operation
            
            Returns
            -------
                Tuple[str, int]
                    A mixed tuple containing:
						
						- The code of the last correction attempt, for the last partial test suite for which a correction was attempted
						- The attempt number at which the correction succeeded
                    
                    An empty tuple is returned if the last series of attempts was not successful
		
			Raises:
            ------
                PromptingSessionNeverPerformedError
                    Occurs if no series of attempts has ever been performed
            
                PromptingSessionInProgressError
                    Occurs if a series of correction attempts is currently in progress
		"""
		if not self._corr_everperf:
			raise PromptingSessionNeverPerformedError()
		if self._corr_inprogr:
			raise PromptingSessionInProgressError()
		
		result: Tuple[str, int] = tuple()
		if self._last_corrpts is not None:
			result = (self._last_corrpts, self._times_tried)
		
		return result


	def start_new_correction(
			self,
			ptsuite_code: str,
			resp_timeout: int
	):
		"""
			Start a new sequence of correction attempts for a partial test suite
            resetting the results of the previous sequence.
            The final success of the correction is NOT guaranteed.
            
            Parameters
            ----------
				ptsuite_code: str
                    A string containing the code of the partial test suite for which
                    correction attempts are to be made
				
				resp_timeout: int
                    An integer representing the timeout in milliseconds after which
                    the response is declared failed
                    
            Raises
            ------
				PromptingSessionInProgressError
                    Occurs if a sequence of correction attempts has already been started
                    but not yet completed
                
                SyntacticallyIncorrectPtsuiteError
                    Occurs if the code of the given partial test suite is syntactically
                    incorrect
		"""
		if (ptsuite_code is None) or (ptsuite_code == ""):
			raise ValueError()
		if resp_timeout < 1:
			raise ValueError()
		if self._corr_inprogr:
			raise PromptingSessionInProgressError()
		
		# Check sintattico della test-suite parziale
		self._is_synt_correct(ptsuite_code)
		
		if not self._corr_everperf:
			self._corr_everperf = True
		self._corr_inprogr = True
		
		# Impostazione delle variabili condivise relative al singolo tentativo
		self._times_tried = 1
		self._try_succ = False
		self._last_corrpts = ptsuite_code
		self._resp_tout = resp_timeout
		
		# Setup del formato del logger
		def_time_format: str = "( {day}-{month}-{year} | {hour}:{min}:{second} )"
		logger_frmt: str
		
		if self._logger is not None:
			try:
				logger_frmt = self._logger.unset_format()
			except FormatNotSetError:
				logger_frmt = "[PtsuiteLintingCorrector] {message} " + def_time_format
			self._logger.set_format(logger_frmt)
	
	
	def perform_corr_try(self) -> str:
		"""
			Performs a single correction attempt on the last version of the partial test suite produced,
			or given if correction was never attempted yet, by submitting it to a specific
			Large Language Model.
			
			ASSUMPTION: It is assumed that the request prompt for the correction has been set
			in the chat object represented by the `ILlmApiAccessor` provided to this corrector.

			Returns
			-------
				str
                    A string containing the last partial test suite produced by the correction request
                    made in this attempt.
                    If the request was interrupted due to a managed error, the value `None` is returned
            
            Raises
            ------
				PromptingSessionNotStartedError
                    Occurs if a series of correction attempts has not been started
                    
                LintingCheckNotPerformedError
                    Occurs if the linting check of the latest version of the
                    partial test suite was not performed before calling this operation
				
				ChatNeverSelectedError
                    Occurs if a chat has never been associated with the provided `ILlmApiAccessor`
            
                ModelNotSelectedError
                    Occurs if no model has been selected for the provided `ILlmApiAccessor`

                ApiConnectionError
                    Occurs if a connection error occurs with the inference platform.
                    The error belongs to its own domain.
                    The `args[0]` attribute, of type string, is used to identify the nature of the error:
					
						- "timeout": The error is related to a connection timeout
                        - "other": The error is of another type (as indicated by the other parts of the `args` attribute)
					
				InvalidPromptError
                    Occurs if the request prompt is invalid for the API represented by the
                    provided `ILlmApiAccessor`
					
				WrongResponseFormatError
                    Occurs if the response format does not conform to the format associated
                    with this PtsuiteLintingCorrector
                
                OSError
                    Occurs if there are problems when opening or writing to the temporary file used
                    for verification
		"""
		if not self._corr_inprogr:
			raise PromptingSessionNotStartedError()
		
		corrtry_ptsuite: str = None
		if self._is_linting_correct():
			self._try_succ = True
			corrtry_ptsuite = self._last_corrpts
		if not self._try_succ:
			try:
				self._logger.log(
					f"Starting the linting correction request (Attempt {self._times_tried}/{self._max_tries}) ..."
				) if self._logger is not None else None
				
				response: str = self._llm_platf.prompt(self._resp_tout)
				
				resp_match: Match[str] = reg_search(self._resp_regex, response, RegexFlags.MULTILINE)
				if resp_match is None:
					self._times_tried += 1
					raise WrongResponseFormatError()
				self._last_corrpts = resp_match.group("gen_code")
				corrtry_ptsuite = self._last_corrpts
				
				self._logger.log("Correction request ENDED") if self._logger is not None else None
				
				self._logger.log("Performing linting check after attempted correction ...") if self._logger is not None else None
				is_lint_correct = self._is_linting_correct()
				if is_lint_correct:
					# Tentativo di correzione riuscito
					self._logger.log(
						f"Partial test suite successfully corrected on attempt {self._times_tried}/{self._max_tries}"
					) if self._logger is not None else None
					self._logger.log("The sequence of correction attempts was completed successfully") if self._logger is not None else None
					self._try_succ = True
					self._corr_inprogr = False
					self._lint_chker.clear_resources()
				else:
					# Tentativo di correzione fallito
					self._times_tried += 1
					self._logger.log("The partial test suite hasn't been corrected") if self._logger is not None else None
			except (ApiResponseError,
			        SaturatedContextWindowError,
			        ResponseTimedOutError) as error:
				# Richiesta al LLM di correzione fallita
				self._logger.log(f"The partial test suite hasn't been corrected (Error: {str(type(error).__name__)})") if self._logger is not None else None
				self._times_tried += 1
				
			if self._times_tried > self._max_tries:
				self._logger.log("The sequence of correction attempts ended in failure") if self._logger is not None else None
				self._last_corrpts = None
				self._corr_inprogr = False
				self._lint_chker.clear_resources()
		else:
			self._corr_inprogr = False
			self._lint_chker.clear_resources()
	
		return corrtry_ptsuite
	
	
	def stop_correction(self):
		"""
			Ends the current sequence of correction attempts by declaring it failed
            
            Raises
            ------
                PromptingSessionNotStartedError
                    Occurs if a correction attempts sequence has not been started
		"""
		if not self._corr_inprogr:
			raise PromptingSessionNotStartedError()
		
		self._last_corrpts = None
		self._try_succ = False
		self._lint_chker.clear_resources()
		
		self._corr_inprogr = False
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================
	
	
	def _is_synt_correct(self, ptsuite_code: str):
		"""
			Performs a syntax check on the first partial test suite provided
            
            Parameters
            ----------
                ptsuite_code: str
                    A string containing the code of the partial test suite to
					correction attempts should be made on
            
            Raises
            ------
                SyntacticallyIncorrectPtsuiteError
                    Checks whether the code of the given partial test suite is syntactically incorrect
                    
                OSError
                    Occurs if there are problems when opening or writing to the temporary file used
                    for verification
		"""
		timestamp: str = str(int(DateTime.now().timestamp() * 1000))
		temp_fname: str = f"temp_{timestamp}.py"
		temp_basepath: str = path_join(
			os_tempdir(),
			"gentests_ai",
			"correction",
			"synt"
		)
		tempfile_path: str = path_join(temp_basepath, temp_fname)
		
		if not os_fdexists(temp_basepath):
			os_mkdirs(temp_basepath)
		with open(tempfile_path, "w") as fptsuite:
			fptsuite.write(ptsuite_code)
			fptsuite.flush()
		try:
			py_compile(
				tempfile_path,
				doraise=True,
				invalidation_mode=Pyc_InvMode.TIMESTAMP
			)
		except PyCompileError:
			os_remove(tempfile_path)
			raise SyntacticallyIncorrectPtsuiteError()
		
		os_remove(tempfile_path)
	
	
	def _is_linting_correct(self) -> bool:
		"""
			Perform a linting check on the latest partial test suite generated
			
			Raises
			------
                OSError
                    Occurs if there are problems when opening or writing to the temporary file used
                    for verification
		"""
		if len(self._lint_chker.check_lintically(self._last_corrpts).keys()) == 0:
			return True
		else:
			return False