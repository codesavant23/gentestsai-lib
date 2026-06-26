from abc import ABC, abstractmethod

# ============== Docker SDK Utilities =============== #
from docker.models.images import Image as DockerImage
# =================================================== #



class IFocalEnvConfigurator(ABC):
	"""
		Represents an object capable of configuring an environment for the execution/testing of a
        focus project.
        
        Each focus environment is primarily used for:
        
            - Verifying the correctness, at the linting level, of the partial test suites of the specific focus project to which the image is linked
			- Calculating the coverage of both sets of test suites (human and LLM)
        
        The installed version of `pylint` is specified by the descendants of this abstract class.
        The installed version of `coverage.py` is specified by the descendants of this abstract class.
	"""
	
	
	@abstractmethod
	def set_default_pyversion(self, python_version: str):
		"""
			Set a new tag for the "python" image to be used if the file
            containing the specific interpreter version for the current focal project,
            does not exist

            Parameters
            ----------
				python_version: str
                    A string containing the tag of the "python" image to be used as a fallback
                    for configuring focal environments.
					It is verified that it contains a version in the following format:
                    `<maj>.<min>.<patch>` or `<maj>.<min>`.

            Raises
            ------
				ValueError
                    Occurs if:
                    
                        - The `python_version` parameter is `None`
                        - The `python_version` parameter is an empty string
                        - The `python_version` parameter does not contain a version in the specified format
		"""
		pass
	
	
	@abstractmethod
	def set_focal_project(
			self,
			proj_name: str,
			full_root: str,
			focal_root: str,
			tests_root: str
	):
		"""
			Set the context data for a new focal project

            Parameters
            ----------
                proj_name: str
                    A string containing the name of the new focal project
            
                full_root: str
					A string containing the Full Project Root Path of the new focal project

                focal_root: str
                    A string containing the Focal Project Root Path of the new focal project

                tests_root: str
                    A string containing the Tests Project Root Path of the new focal project
					
			Raises
            ------
                ValueError
                    Occurs if:
                    
                        - The `proj_name` parameter is `None` or an empty string
						- The `full_root` parameter is `None` or an empty string
                        - The `focal_root` parameter is `None` or an empty string
                        - The `tests_root` parameter is `None` or an empty string
		"""
		pass
	
	
	@abstractmethod
	def set_path_prefix(self, path_prefix: str):
		"""
			Set a new path prefix to be used as the Full Project Root Path in the Docker-compatible
			container, which will be instantiated later, by combining it with the Full Project
			Directory of the currently selected project.

			Parameters
			----------
				path_prefix: str
                    A string containing the new path prefix to be prepended to the Full Project Directory of the
                    selected focal project to construct the Full Project Root Path within the container

			Raises
            ------
                ValueError
                    Occurs if the provided path prefix is not in Linux format
			
				FocalProjectNotSetError
                    Occurs if a focal project is not set before calling this operation

                DefaultPythonVersionNotSetError
                    Occurs if no default tag has been set for the "python" image
                    before calling this operation
		"""
		pass
	
	
	@abstractmethod
	def build_image(
			self,
			wants_dockign: bool = True
	) -> DockerImage:
		"""
			Create a Docker image corresponding to the focal environment of the last project set up;
            this image will be used to instantiate the container that serves as the actual environment.
            
            The created Docker image has the following string as its tag:
                "<tag_prefix>_<project_name>:latest"
				
			where `<tag_prefix>` is the prefix chosen for the tag and `<project_name>` is the name of the focal project for which the image is being created
			
			In the focal environment:
                - The following software is installed:
                
                    - `curl` in the latest version
                    - `git` in the latest version
                    - `python` with a version based on the choice (from the focal project, or falling back to the default tag set in this configurator)
					- `pylint` with a version based on the selection (from the focal project, or fallback to the default version specified by descendants)
                    - `coverage.py` with a version based on the selection (from the focal project, or fallback to the default version specified by descendants)
                    
				- The following environment variables are defined:
                    
                    - `PYTHON_VERSION`: The version of the Python interpreter in the Focal environment
                    - `FULL_ROOT`: The full project root path within the Focal environment
					- `FOCAL_ROOT`: The Focal Project Root Path within the focal environment
                    - `TESTS_ROOT`: The Tests Project Root Path within the focal environment
                    - `GENTESTS_ROOT`: The Gen-tests Project Root Path within the focal environment
					- `LINTTOOLS_DIR`: The name of the folder containing the linting tools
                
                - All dependencies of the focal project, whether Python or non-Python, are installed,
                  specified via the files in its Env-config Project Root Path

			Parameters
            ----------
                wants_dockerignore: bool
                    Optional. Default = `True`. A boolean indicating whether to write a file
                    ".dockerignore" before building the focal environment image.
					If the specified focal project already has a ".dockerignore" file, it will be
                    preserved and overwritten at the end by deleting the ".dockerignore" file written
                    by this operation

            Returns
            -------
				DockerImage
                    A `docker.models.images.Image` object representing the Docker image to be used to
                    instantiate the container with the environment configured for the set focal project

			Raises:
            ------
				FocalProjectNotSetError
                    Occurs if no focal project is set before calling this operation

                DefaultPythonVersionNotSetError
                    Occurs if no default tag has been set for the "python" image
                    before calling this operation
		"""
		pass