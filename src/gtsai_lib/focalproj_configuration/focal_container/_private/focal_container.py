from typing import Tuple

from io import BytesIO
# ============== OS Utilities ============== #
from os import (
	makedirs as os_mkdirs,
	environ as os_getenv
)
from shutil import rmtree as os_dremove
# ========================================== #
# ============ Path Utilities ============ #
from os.path import (
	sep as path_sep,
	altsep as path_altsep,
	join as path_join
)
_PATH_SEPS: str = f"{path_sep}{path_altsep if path_altsep is not None else ''}"
# ======================================== #
# ============ Docker SDK Utilities ============ #
from docker import (
	from_env as docker_getclient,
	DockerClient
)
from docker.models.images import Image as DockerImage
from docker.models.containers import (
	Container as DockerContainer,
	ExecResult as DockerContainerExecResult
)
# ============================================== #

from ..exceptions import (
	ContainerNotRunningError,
	ContainerAlreadyRunningError,
	CommandNeverExecutedError
)



class FocalContainer:
	"""
		Represents an object capable of managing a Docker-compatible container associated
		with a specific focal project.
        Each Docker-compatible container is built based on a pre-configured image
        designed to host the focal project to which it is linked.
		
		Specifically, the container is used for the following purposes:
        
            - Verifying the correctness, at the linting level, of the generated partial test suites
            - Calculating the coverage of both sets of test suites (human and LLM)
	"""

	def __init__(
			self,
			docker_image: DockerImage,
			full_root: str,
			path_prefix: str,
			results_dirname: str = "gtsai__results",
			stop_timeout: int=1
	):
		"""
			Creates a new FocalContainer based on the pre-configured image,
            from which the Docker-compatible container will be instantiated

            Parameters
            ----------
				docker_image: DockerImage
                    A `docker.models.images.Image` object representing the pre-configured container image
                    on which the managed Docker-compatible container will be based
                    
                full_root: str
					A string containing the Full Project Root Path of the target project for which
					the Docker-compatible container will be managed

                path_prefix: str
                    A string containing the path prefix, set during image construction, which represents the Full Project Root Path within the managed Docker container
					
				results_dirname: str
					Optional. Default = `"gtsai__results"`. A string representing the name of the volume directory,
					within the `path_prefix`, which will contain the files produced by the target environment as results
	
				stop_timeout: int
                    Optional. Default = `1`. An integer indicating the timeout value (in seconds)
                    for stopping the Docker-compatible container managed by this FocalContainer

			Raises:
            ------
                ValueError
                    Occurs if:
                    
                        - The `docker_image` parameter is `None`
                        - The `full_root` parameter is `None` or an empty string
						- The `path_prefix` parameter is `None` or an empty string
                        - The `results_dirname` parameter is `None` or an empty string
                        - The `stop_timeout` parameter is less than 1
		"""
		if (
			(docker_image is None) or
			(full_root is None) or (full_root == "") or
			(path_prefix is None) or (path_prefix == "") or
			(stop_timeout < 1)
		):
			raise ValueError()
		
		self._docker: DockerClient = None
		try:
			docker_host: str = os_getenv["DOCKER_HOST"]
			self._docker = DockerClient(base_url=docker_host)
		except KeyError:
			self._docker = docker_getclient()

		self._image = docker_image
		self._full_root: str = full_root.rstrip(_PATH_SEPS)

		self._path_prefix: str = path_prefix
		
		self._results_dir: str = results_dirname

		self._timeout: int = stop_timeout

		self._environ: DockerContainer = None
		self._running: bool = False
		
		self._cmd_ever_execd: bool = False
		self._lexec_exitcode: int = -1
		self._lexec_stdout: str = None
		self._lexec_stderr: str = None


	def start_container(self):
		"""
			Starts the Docker container based on the image associated with this FocalContainer.
            If the Docker-compatible container managed by this FocalContainer is already running,
            it must first be terminated before it can be restarted.

			Raises
            ------
                ContainerAlreadyRunningError
                    If the Docker container managed by this FocalContainer is already running when
                    this operation is called
		"""
		if self._running:
			raise ContainerAlreadyRunningError()
		
		results_path: str = path_join(self._full_root, self._results_dir)
		
		os_dremove(results_path, ignore_errors=True)
		os_mkdirs(results_path)

		self._environ = self._docker.containers.run(
			image=self._image,
			detach=True,
			volumes={
				results_path: {
					"bind": f"{self._path_prefix}/{self._results_dir}",
					"mode": "rw"
				}
			}
		)

		self._running = True
		
		
	def put_tararchive(self, dest_path: str, tar_stream: BytesIO):
		"""
			Extracts the contents of the TAR stream, provided as an argument, into the
			Docker-compatible container at the specified path
            
            Parameters
            ----------
				dest_path: str
                    A string representing the destination path for the contents
                    of the provided TAR stream.
					ASSUMPTION: It is assumed that `dest_path` is a path that exists within the target container
                
                
                tar_stream: BytesIO
                    A `BytesIO` object representing the TAR stream from which to extract
                    the contents into the container
					
			Raises:
            ------
                ValueError
                    Occurs if:
                        
                        - The `dest_path` parameter is `None` or an empty string
                        - The `tar_stream` parameter is `None`
		"""
		if (dest_path is None) or (dest_path == ""):
			raise ValueError()
		if tar_stream is None:
			raise ValueError()
		
		self._environ.put_archive(dest_path, tar_stream)


	def execute(
			self,
			command: str,
			privileged: bool = False
	):
		"""
			Executes the shell command provided as an argument within the Docker container
			managed by this FocalContainer; and stores the resulting standard output,
			standard error, and exit code

            Parameters
            ----------
				command: str
                    A string containing the shell command to be executed inside the running
                    Docker container managed by this FocalContainer

                privileged: bool
					Optional. Default = `False`. A boolean specifying whether the command
					should be executed with privileges

            Raises
            ------
                ValueError
                    Occurs if:
					
						- The `command` parameter is None
                        - The `command` parameter is an empty string
            
                ContainerNotRunningError
                    If the Docker container managed by this FocalContainer is not running when
                    this operation is called
		"""
		result: DockerContainerExecResult = self._environ.exec_run(
			command,
			privileged=privileged,
			demux=True
		)
		output: Tuple[bytes, bytes] = result.output
		
		self._lexec_exitcode = result.exit_code
		if output[0] is not None:
			self._lexec_stdout = output[0].decode("utf-8")
		else:
			self._lexec_stdout = None
		
		if output[1] is not None:
			self._lexec_stderr = output[1].decode("utf-8")
		else:
			self._lexec_stderr = None
		
		if not self._cmd_ever_execd:
			self._cmd_ever_execd = True


	def stop_container(self):
		"""
			The Docker container managed by this FocalContainer has stopped running.

            Raises
            ------
                ContainerNotRunningError
                    If the Docker container managed by this FocalContainer is not running
                    when this operation is called
		"""
		if not self._running:
			raise ContainerNotRunningError()

		self._environ.stop(timeout=self._timeout)
		self._environ.remove(
			v=True,
			force=True
		)
		del self._environ
		self._environ = None

		self._running = False


	def get_last_stdout(self) -> str:
		"""
			Returns the standard output for the last command executed
			within the last container
            
            Raises
            ------
                CommandNeverExecutedError
                    If no shell command has ever been executed before calling
                    this operation
		"""
		if self._cmd_ever_execd:
			raise CommandNeverExecutedError()
		
		return self._lexec_stdout


	def get_last_stderr(self) -> str:
		"""
			Returns the standard error associated with the last command executed
            inside the last container
            
            Raises
            ------
                CommandNeverExecutedError
                    If no shell command has ever been executed before
                    calling this operation
		"""
		if self._cmd_ever_execd:
			raise CommandNeverExecutedError()
		
		return self._lexec_stderr


	def get_last_exitcode(self) -> int:
		"""
			Returns the exit code for the last command executed
            inside the last container
            
            Raises
            ------
                CommandNeverExecutedError
                    If no shell command has ever been executed
                    before calling this operation
		"""
		if self._cmd_ever_execd:
			raise CommandNeverExecutedError()
		
		return self._lexec_exitcode