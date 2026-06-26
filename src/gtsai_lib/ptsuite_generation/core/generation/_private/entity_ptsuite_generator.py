from typing import Tuple

# ============= RegEx Utilities ============ #
from regex import (
	search as reg_search,
	Match,
	RegexFlag as RegexFlags,
)
# ========================================== #

from c23_logger import ATemporalFormattLogger
from c23_logger.exceptions import FormatNotSetError

from llm_access.llm_apiaccessor import ILlmApiAccessor
from llm_access.llm_apiaccessor.exceptions import (
	ResponseTimedOutError,
	ApiResponseError,
	SaturatedContextWindowError,
)

from ...exceptions import (
	WrongResponseFormatError,
	PromptingSessionInProgressError,
	PromptingSessionNotStartedError,
	PromptingSessionNeverPerformedError
)



class EntityPtsuiteGenerator:
	"""
		Represents an object capable of instructing an LLM to generate a partial test suite,
        relating to a single autonomous entity.
		
		Public Class Attributes:
            - `GENCODE_PATT` (str) : Represents the default regex pattern to be used to identify the code in the response to a generation attempt
	"""
	GENCODE_PATT: str = r"```python\n?(?P<gen_code>[\s\S]+)\n?```"

	def __init__(
			self,
			max_tries: int,
			llm_accsor: ILlmApiAccessor,
			logger: ATemporalFormattLogger = None,
			resp_format: str = None
	):
		"""
			It creates a new EntityPtsuiteGenerator and associates it with an `ILlmApiAccessor`
            which it will use to send generation requests to the LLMs that will be, or have been,
            configured.
			
			It may also be associated with the logger used to record the stages of each
            generation attempt, and with a response format different from the default
            (default format: `self.GENCODE_PATT`)

            Parameters
            ----------
				max_tries: int
                    An integer indicating the maximum number of attempts to make
                    in the requests
            
                llm_accsor: ILlmApiAccessor
                    An `ILlmApiAccessor` object that will be used to perform generation requests
					
				logger: ATemporalFormattLogger
                    Optional. Default = `None`. An `ATemporalFormattLogger` object representing the logger
                    to be used to record the stages of each generation attempt (not to record the stages
                    of the LLM request for each attempt)
					
				resp_format: str
                    Optional. Default = `None`. A RegEx string containing the format to be used to identify
                    the code resulting from the generation attempts made.
                    It must contain a named group called "gen_code"
					
			Raises:
            ------
				ValueError
                    Occurs if:
                    
                        - The `max_tries` parameter is less than 1
                        - The `response_format` parameter is provided but does not contain a named group called "gen_code"
		"""
		if max_tries < 1:
			raise ValueError()
		
		self._resp_regex: str =	self.GENCODE_PATT
		if resp_format is not None:
			if resp_format.find("(?P<gen_code>") == -1:
				raise ValueError()
			self._resp_regex = resp_format
		
		self._gen_everperf: bool = False
		self._gen_inprogr: bool = False
		self._times_tried: int = 0
		self._try_succ: bool = False
		self._resp_tout: int = 0
		
		self._last_genpts: str = ""
		self._max_tries: int = max_tries
		
		self._llm_platf: ILlmApiAccessor = llm_accsor
		self._logger: ATemporalFormattLogger = logger
		
		
	def has_gen_terminated(self) -> bool:
		"""
			Checks whether the current generation attempt has ended, either because
			generation was successful or because the maximum number of attempts
			has been reached
            
            Returns
            -------
                bool
					A Boolean indicating whether the previously started attempt series,
                    has ended
                    
            Raises
            ------
                PromptingSessionNeverPerformedError
                    Occurs if a generation attempt series has never been started
		"""
		if not self._gen_everperf:
			raise PromptingSessionNeverPerformedError()
		
		return not self._gen_inprogr
	
	
	def has_gen_succ(self) -> bool:
		"""
			Checks whether the last generation attempt was successful so that
			a partial test suite has been generated successfully

            Returns
            -------
				bool
                    A boolean indicating whether the last partial test suite that
                    was attempted to be generated was successful

			Raises
            ------
                PromptingSessionNeverPerformedError
                    Occurs if a series of generation attempts has never been started
            
                PromptingSessionInProgressError
                    Occurs if a series of generation attempts is not currently in progress
		"""
		if not self._gen_everperf:
			raise PromptingSessionNeverPerformedError()
		if self._gen_inprogr:
			raise PromptingSessionInProgressError()
		
		return self._try_succ


	def get_lastgen(self) -> Tuple[str, int]:
		"""
			Returns a tuple containing:
                
                - The code resulting from the last attempt to generate a partial test suite
                - The attempt number at which the generation was successful

            To verify the success of the last sequence of generation attempts, you
            must use the `.has_gen_succ(...)` operation
            
            Returns
            -------
                Tuple[str, int]
                    A mixed tuple containing:
                    
                        - The code of the last generation attempt of the last requested partial test suite
                        - The attempt number at which the generation was successful
                    
                    An empty tuple is returned if the last sequence of attempts was not successful
                    
			Raises
			------
                PromptingSessionNeverPerformedError
                    Occurs if a sequence of generation attempts has never been started
            
                PromptingSessionInProgressError
                    Occurs if a sequence of generation attempts is not currently in progress
		"""
		if not self._gen_everperf:
			raise PromptingSessionNeverPerformedError()
		if self._gen_inprogr:
			raise PromptingSessionInProgressError()
		
		result: Tuple[str, int] = tuple()
		if self._last_genpts != "":
			result = (self._last_genpts, self._times_tried)
			
		return result
		
		
	def start_new_generation(
			self,
			resp_timeout: int
	):
		"""
			Start a new sequence of generation attempts of a partial test suite
            resetting the results of the previous generation sequence.
            The final success of the generation is NOT guaranteed.
            
            Parameters
            ----------
				resp_timeout: int
                    An integer representing the timeout in milliseconds after which
                    the response is declared failed
					
			Raises
            ------
                PromptingSessionInProgressError
                    Occurs if a generation attempt sequence has already been started
                    but not yet completed
		"""
		if self._gen_inprogr:
			raise PromptingSessionInProgressError()
		
		if not self._gen_everperf:
			self._gen_everperf = True
		self._gen_inprogr = True
		
		self._times_tried = 1
		self._try_succ = False
		self._last_genpts = ""
		self._resp_tout = resp_timeout
		
		# Setup del formato del logger
		def_time_format: str = "( {day}-{month}-{year} | {hour}:{min}:{second} )"
		logger_frmt: str
		try:
			logger_frmt = self._logger.unset_format()
		except FormatNotSetError:
			logger_frmt = "[EntityPtsuiteGenerator] {message} " + def_time_format
		self._logger.set_format(logger_frmt)


	def perform_gen_try(self) -> str:
		"""
			Performs a single generation attempt for the partial test suite requested, by prompting
			a specific Large Language Model.
			
			ASSUMPTION: It is assumed that the request prompt for the generation has been set
			in the chat object represented by the `ILlmApiAccessor` provided to this generator.

			Returns
			-------
				str
                    A string containing the partial test suite produced by this generation attempt
                    if the request has been successfull.
                    If the request was interrupted due to a managed error, the value `None` is returned
			
			Raises
			------
				PromptingSessionNotStartedError
                    Occurs if a series of generation attempts has not been started
				
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
                    with this EntityPtsuiteGenerator
		"""
		if not self._gen_inprogr:
			raise PromptingSessionNotStartedError()
		
		gentry_ptsuite: str = None
		if not self._try_succ:
			try:
				self._logger.log(
					f"Starting generation attempt (Attempt {self._times_tried}/{self._max_tries}) ..."
				) if self._logger is not None else None
				
				response: str = self._llm_platf.prompt(self._resp_tout)
				
				resp_match: Match[str] = reg_search(self._resp_regex, response, RegexFlags.MULTILINE)
				if resp_match is None:
					self._times_tried += 1
					raise WrongResponseFormatError()
				
				self._last_genpts = resp_match.group("gen_code")
				gentry_ptsuite = self._last_genpts
				
				self._try_succ = True
				self._gen_inprogr = False
				
				if self._logger is not None:
					self._logger.log(
						f"Attempt no. {self._times_tried}/{self._max_tries} was successful"
					)
					self._logger.log(
						f"End of the series of generation attempts"
					)
			except (ApiResponseError,
			        SaturatedContextWindowError,
			        ResponseTimedOutError) as error:
				self._logger.log(f"The partial test suite was not generated (Error: {str(type(error).__name__)})") if self._logger is not None else None
				self._times_tried += 1
				
			if self._times_tried > self._max_tries:
				self._logger.log("The series of generation attempts ended in failure") if self._logger is not None else None
				self._logger.log(
					f"End of the series of generation attempts"
				) if self._logger is not None else None
				self._last_genpts = ""
				self._gen_inprogr = False
		
		return gentry_ptsuite
	
	
	def stop_generation(self):
		"""
			Ends the current sequence of generation attempts
			by declaring it as failed for this generator
            
            Raises
            ------
                PromptingSessionNotStartedError
                    Occurs if a sequence of generation attempts has not been started
		"""
		if not self._gen_inprogr:
			raise PromptingSessionNotStartedError()
		
		self._last_genpts = ""
		self._try_succ = False
		
		self._gen_inprogr = False