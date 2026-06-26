from typing import List, Dict
from abc import ABC, abstractmethod



class IDockfBuilder(ABC):
	"""
		Represents an object capable of building Dockerfiles incrementally.
        Upon instantiation of each IDockfBuilder, it is already initialized to begin the
        incremental construction of the first Dockerfile.
        
        The implementation technology for storing instructions is specified by the
        implementers of this interface
	"""

	
	@abstractmethod
	def new_dockerfile(self):
		"""
			Initialize the builder to create a new Dockerfile by clearing all instructions
            from the previously built Dockerfile
		"""
		pass
		

	@abstractmethod
	def set_base_image(self, base_image: str):
		"""
			Sets a new base image on which the next Dockerfile to be built will be based.
            Calling this method is equivalent to adding or modifying the `FROM base_image` instruction
            in the resulting Dockerfile.

            Parameters
            ----------
				base_image: str
                    A string containing the name of the base image for images derived
                    from the Dockerfile that will be built subsequently.
					
			Raises
            ------
                ValueError
                    Occurs if:
                        
                        - The `base_image` parameter is `None`
                        - The `base_image` parameter is an empty string
		"""
		pass


	@abstractmethod
	def set_envvar(self, var_name: str, value: str):
		"""
			Adds a definition for a shell environment variable (also visible in the Dockerfile).
            Calling this method is equivalent to adding an `ENV var_name=value` statement
            to the resulting Dockerfile

            Parameters
            ----------
				var_name: str
                    A string containing the environment variable whose definition is to be added

                value: str
                    A string containing the value to be set for the environment variable
					
			Raises
            ------
                ValueError
                    Occurs if:
                        
                        - The `var_name` parameter is `None` or an empty string
                        - The `value` parameter is `None` or an empty string
		"""
		pass
	
	
	@abstractmethod
	def add_shell(
			self,
			shell_touse: str,
			args: List[str]=None
	):
		"""
			Adds a declaration specifying the shell to be used for subsequent command executions,
            which will be added to the Dockerfile currently being built.
            Calling this method is equivalent to adding the `SHELL` instruction to the resulting
            Dockerfile.
			
			Parameters
            ----------
                shell_touse: str
                    A string containing the path to the shell executable to be used

                args: List[str]
					Optional. Default = `None`. A list of strings containing the arguments
					to be provided to the shell for executing commands.
            
            Raises
            ------
				ValueError
                    Occurs if:
                        
                        - The `shell_touse` parameter is `None`
                        - The `shell_touse` parameter is an empty string
                        - The `args` parameter is an empty list
		"""
		pass


	@abstractmethod
	def add_shellcmd(self, shell_cmd: str):
		"""
			Adds the execution of a shell command to the Dockerfile that will be built.
            Calling this method is equivalent to adding a `RUN shell_cmd` instruction
            to the resulting Dockerfile.
            A new layer is added to the Dockerfile.

			Parameters
            ----------
                shell_cmd: str
                    A string containing the command to be executed
					
			Raises
            ------
                ValueError
                    Occurs if:
                        
                        - The `shell_cmd` parameter is `None`
                        - The `shell_cmd` parameter is an empty string
		"""
		pass


	@abstractmethod
	def set_global_args(self, global_args: Dict[str, str]):
		"""
			Set new global arguments for the next Dockerfile to be built.
            Calling this method is equivalent to adding or modifying the `ARG <key>=<value>` directive
            in the resulting Dockerfile, corresponding to the `global_args` key named "`<key>`".
			
			Any key set to `None` is equivalent to removing the corresponding global argument.

			Parameters
			----------
				global_args: Dict[str, str]
                    A string-indexed dictionary containing the global arguments
                    to be set in the resulting Dockerfile
					
			Raises
            ------
                ValueError
                    Occurs if:
                        
                        - The `global_args` parameter is `None`
                        - The `global_args` parameter is an empty dictionary
		"""
		pass
	
	
	@abstractmethod
	def add_copy(self, sources: List[str], dest: str):
		"""
			Adds a request to copy the contents of the directories to the Dockerfile that is subsequently built.
            Calling this method is equivalent to adding a `COPY` instruction to the resulting Dockerfile.
            A new layer is added to the Dockerfile
            
            Parameters
            ----------
				sources: List[str]
                    A list of strings representing the paths whose contents are to be copied into
                    the destination
                    
                dest: str
                    A string representing the path to which the contents of the sources are to be copied
					
			Raises
            ------
                ValueError
                    Occurs if:
						
						- The `sources` parameter is `None` or an empty list
                        - If any of the paths in `sources` is `None` or an empty string
                        - The `dest` parameter is `None` or an empty string
		"""
		pass
	
	
	@abstractmethod
	def add_workdir(self, dest: str):
		"""
			Adds a request to change the working directory to the specified directory.
            Calling this method is equivalent to adding a `WORKDIR` instruction to the resulting Dockerfile.
            A new layer is added to the Dockerfile.
            
            Parameters
            ----------
				dest: str
                    A string representing the destination path to move to (during the build
                    of the image resulting from the subsequent Dockerfile)
					
			Raises
            ------
                ValueError
                    Occurs if:
                        
                        - The `dest` parameter has a value of `None`
                        - The `dest` parameter is an empty string
		"""
		pass
	
	
	@abstractmethod
	def set_entrypoint(
			self,
	        entry_cmd: str,
			def_args: List[str]=None
	):
		"""
			Sets the entrypoint (main process) of the generated containers based on the Dockerfile
            built subsequently, and optionally also its default arguments.
			Calling this method is equivalent to adding/modifying the `ENTRYPOINT` and `CMD` directives
			in the resulting Dockerfile.
			The `ENTRYPOINT` directive is written in Exec-Form.
			
			Parameters
			----------
				entry_cmd: str
                    A string containing the command to be executed as the container's main process, based on
                    the image built from the Dockerfile built subsequently
					
				def_args: List[str]
                    Optional. Default = `None`. A list of strings containing the default arguments to pass
                    to the command to be executed as the main process (these are written in the `CMD` instruction).
                    They can be overridden by the `docker run` command
					
			Raises
            ------
                ValueError
                    Occurs if:
                    
                        - The `entry_cmd` parameter is an empty string
                        - The `def_args` parameter is an empty string
		"""
		pass
	
	
	@abstractmethod
	def build_dockerfile(
			self,
	        dockf_path: str,
	):
		"""
			Builds the Dockerfile by writing it to the specified path. The file at the specified path
			is truncated and then written.
			
			The defined environment variables are all written at the beginning after selecting
			the base image and the Dockerfile's global variables

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
		pass