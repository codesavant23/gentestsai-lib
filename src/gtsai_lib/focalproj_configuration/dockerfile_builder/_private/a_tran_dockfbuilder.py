from typing import List
from abc import abstractmethod
from ._a_base_dockfbuilder import _ABaseDockfBuilder

from ..exceptions import (
	TransactionStartedError,
	TransactionNotStartedError
)



class ATransactDockfBuilder(_ABaseDockfBuilder):
	"""
		Represents a "transactional" `IDockfBuilder`, meaning it allows you to write
        shell command transactions (multiple shell commands executed within a single `RUN` layer).
        
        The implementation technology for storing instructions is specified by the
        descendants of this abstract class
	"""
	
	def __init__(self):
		"""
			Creates a new ATransactDockfBuilder
		"""
		super().__init__()
		
		self._tran_open: bool = False
		self._tran_cmds: List[str] = list()
		
		
	def begin_cmds_tran(self):
		"""
			Starts a new transaction of shell commands to be included in a single `RUN` statement.
            The transaction ensures that a single, new layer is added to the Dockerfile.

			Raises
            ------
                TransactionStartedError
                    Occurs if another transaction is already in progress
		"""
		self._assert_transaction_not_started()

		self._tran_open = True
		self._tran_cmds.clear()


	def add_shellcmd_step(
			self,
			shell_cmd: str
	):
		"""
			Adds a new shell command to the current transaction

            Parameters
            ----------
				shell_cmd: str
                    The shell command to add to the current transaction

            Raises
            ------
                TransactionNotStartedError
                    Occurs if no transaction has been started
		"""
		self._assert_transaction_started()

		self._tran_cmds.append(shell_cmd)


	def commit_cmds_tran(self):
		"""
			Finalizes the shell command transaction that was started and writes all shell commands
            into a single `RUN` statement.
            All commands are concatenated using the `"&&"` separator.
			
			If no commands have been entered into the transaction, then this operation
			is equivalent to a no-op

			Raises
			------
			    TransactionNotStartedError
			        If no transaction has been started
		"""
		self._assert_transaction_started()

		if len(self._tran_cmds) > 0:
			self._ap__add_instr(f"RUN {' && '.join(self._tran_cmds)}")

		self._tran_open = False
	
	
	def build_dockerfile(self, dockf_path: str):
		"""
			Builds the Dockerfile by writing it to the specified path.
            The file at the specified path is truncated and then overwritten.
            
            All shell command transactions are forcibly closed.
            
            The defined environment variables are all written at the beginning after selecting
			of the base image and the Dockerfile's global variables.

            Parameters
            ----------
                dockf_path: str
                    A string representing the path of the file that will contain the Dockerfile
                    built incrementally from the instantiation of this IDockfBuilder
					or the last call to `.new_dockerfile(...)`

            Raises
            ------
                BaseImageNotSetError
                    If no base image has been set when this operation is called
		"""
		try:
			self.commit_cmds_tran()
		except TransactionNotStartedError:
			pass
		super().build_dockerfile(dockf_path)
	
	
	##	============================================================
	##						ABSTRACT METHODS
	##	============================================================
	
	
	@abstractmethod
	def _ap__new_dockerf_spec(self):
		pass
	
	
	@abstractmethod
	def _ap__add_instr(self, instr: str):
		pass
	
	
	@abstractmethod
	def _ap__get_dockf_body(self) -> str:
		"""
			Returns the main body of the current Dockerfile to write it to a file.
            The "main body" refers to all instructions that are not:
            
                - FROM
                - ARG
                - ENTRYPOINT or CMD
			
			This method ensures that any ongoing shell command transaction has already been closed.

			Returns
			-------
				str
                    A string representing the main body of the Dockerfile that
                    contains its instructions
		"""
		pass
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================


	def _assert_transaction_started(
			self,
			err_msg: str = "No shell command transactions have been initiated!"
	):
		if not self._tran_open:
			raise TransactionNotStartedError(err_msg)


	def _assert_transaction_not_started(
			self,
			err_msg: str = "A shell command is already in progress!"
	):
		if self._tran_open:
			raise TransactionStartedError(err_msg)