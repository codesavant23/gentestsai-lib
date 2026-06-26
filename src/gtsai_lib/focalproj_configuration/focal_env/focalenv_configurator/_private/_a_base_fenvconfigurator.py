from typing import List, Tuple, Dict
from abc import abstractmethod
from .. import IFocalEnvConfigurator

# ============== Docker SDK Utilities =============== #
from docker import (
	from_env as docker_getclient,
	DockerClient
)
from docker.models.images import Image as DockerImage
# =================================================== #
# ============ RegEx Utilities ============ #
from regex import (
	search as reg_search,
	Match,
)
# ========================================= #
# ============== OS Utilities ============== #
from os import (
	environ as os_envvar,
	rename as os_rename,
)
from shutil import rmtree as os_dremove
from os.path import exists as os_fdexists
# ========================================== #
# ============ Path Utilities ============ #
from os.path import (
	join as path_join,
	split as path_split,
	sep, altsep
)
from pathlib import (
	Path as SystemPath,
	PosixPath
)
from shutil import (
	copytree as os_dcopy
)
_PATH_SEPS: str = f"{sep}{altsep if altsep is not None else ''}"
# ======================================== #
# ============== JSON Utilities ============== #
from json import JSONDecoder
# ============================================ #

from ....dockerfile_builder import (
	ATransactDockfBuilder,
	SimpleTransactDockfBuilder
)
from ..buildcache_cleaner import (
	IBuildCacheCleaner,
	BuildCacheCleanerFactory, EContainerManager
)

from ....exceptions import (
	FocalProjectNotSetError,
	DefaultPythonVersionNotSetError
)



class _ABaseFocalEnvConfigurator(IFocalEnvConfigurator):
	"""
		Represents a basic `IFocalEnvConfigurator`, containing the logic common
		to every `IFocalEnvConfigurator`.
		
		Public Class Attributes:
            - `PATH_PREFIX` (str): The default prefix of the path, within the Docker container, to which the contents of the focal project will be mounted to make it accessible within the container.
		
		The installed version of `pylint` is specified by the descendants of this abstract class.
        The installed version of `coverage.py` is specified by the descendants of this abstract class.
        The package of additional software installed, independent of the focal project, is specified
        by the descendants of this abstract class
	"""
	
	_PYVERS_PATT: str = r"[0-9]+\.[0-9]+(\.[0-9]+)?"
	_LINUXPATH_PATT: str = r"^(?P<path_prefix>(/[\w.-]+/?)+)$"
	PATH_PREFIX: str = "/app"
	
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
			pref_contman: EContainerManager = None
	):
		"""
			Creates a new _ABaseFocalEnvConfigurator and associates it with:
                
                - The `ATransactDockfBuilder` to be used to build the image's Dockerfile;
                - The Env-Config Project Root Path structure;
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
                    Optional. Default = `None`. A string representing the initial path prefix, if any,
                    to be used for images generated with this IFocalEnvConfigurator
                    
                pref_contman: EContainerManager
                    Optional. Default = `None`. An `EContainerManager` value indicating the container manager
                    to be used for managing focal environments.
                    If `None` is provided (or no value is provided), the primary container manager installed
                    on the operating system is considered selected. (See "Container Manager Selection Criteria"
                    in the full documentation)
					
			Raises:
            ------
                ValueError
                    Occurs if:

                        - The `tag_prefix` parameter is `None` or an empty string
                        - The `gentests_dir` parameter is `None` or an empty string
						- The `envconfig_dir` parameter is `None` or an empty string
                        - The `dockerfile_fname` parameter is `None` or an empty string
                        - The `py_vers_fname` parameter is `None` or an empty string
						- The `deps_files` parameter is `None`, is an empty tuple; or one of its elements is `None` or at least one is an empty string
                        - The `tools_root` parameter is `None`, is an empty string, or is an invalid path
						- The `linttools_dir` parameter is `None`, an empty string, or the directory does not exist in `tools_root`
                        - The `path_prefix` parameter is an empty string or an invalid Linux path
		"""
		self._check_initargs(
			image_prefix,
			gentests_dir, envconfig_dir, dockerfile_fname, py_vers_fname, deps_files,
			tools_root, linttools_dir, path_prefix
		)
		
		self._json_dec: JSONDecoder = JSONDecoder()
		
		self._project_set: bool = False
		self._def_pyvers_set: bool = False

		self._docker: DockerClient = None
		try:
			docker_host: str = os_envvar["DOCKER_HOST"]
			self._docker = DockerClient(base_url=docker_host)
		except KeyError:
			self._docker = docker_getclient()
			
		self._cache_cner: IBuildCacheCleaner
		if pref_contman is not None:
			self._cache_cner = BuildCacheCleanerFactory.obtain(pref_contman)
		else:
			self._cache_cner = BuildCacheCleanerFactory.obtain()
		
		self._dockf_builder: ATransactDockfBuilder = SimpleTransactDockfBuilder()
		self._dockf_builder.new_dockerfile()
		self._dockf_fname: str = dockerfile_fname
		
		self._tag_prefix: str = image_prefix

		self._envconfig_dir: str = envconfig_dir
		self._gentests_dir: str = gentests_dir

		self._path_prefix: str = self.PATH_PREFIX
		if path_prefix is not None:
			self._path_prefix = path_prefix.rstrip("/")

		# The name of the focal project set
		self._proj_name: str = None
		# The actual full project root path
		self._orig_full_root: str = None
		# The full project root path inside the container
		self._full_root: str = None
		# The Focal Project Root Path inside the container
		self._focal_root: str = None
		# The Tests Project Root Path inside the container
		self._tests_root: str = None
		# The Env-config project root path inside the container
		self._envconfig_root: str = None
		# The Gen-tests project root path inside the container
		self._gentests_root: str = None
		
		# File containing the Python interpreter version
		self._py_vers_fname: str = py_vers_fname
		self._py_vers_path: str = None
		
		# File (JSON dictionary) containing the list of Python dependencies
		self._py_deps_fname: str = deps_files[0]
		self._py_deps_path: str = None
		
		# File containing list of external dependencies
		self._ext_deps_fname: str = deps_files[1]
		self._ext_deps_path: str = None
		
		# Script files before and after installation of external dependencies
		self._prescr_fname: str = deps_files[2]
		self._prescr_path: str = None
		self._postscr_fname: str = deps_files[3]
		self._postscr_path: str = None
		self._prescrpy_fname: str = deps_files[4]
		self._prescrpy_path: str = None
		self._postscrpy_fname: str = deps_files[5]
		self._postscrpy_path: str = None
		
		# Path to the tools in the production environment
		self._tools_root: str = tools_root.rstrip(_PATH_SEPS)
		# Directory of tools for calculating code coverage
		self._covtools_dir: str = covtools_dir
		# Directory of tools for linting verification
		self._linttools_dir: str = linttools_dir
	
	
	def set_default_pyversion(self, python_version: str):
		vers_found: Match[str] = reg_search(self._PYVERS_PATT, python_version)
		if vers_found is None:
			raise ValueError()
		
		self._def_pyvers = python_version
		self._def_pyvers_set = True
	
	
	def set_focal_project(
			self,
			proj_name: str,
	        full_root: str,
			focal_root: str,
			tests_root: str
	):
		if (proj_name is None) or (proj_name == ""):
			raise ValueError()
		if (full_root is None) or (full_root == ""):
			raise ValueError()
		if (focal_root is None) or (focal_root == ""):
			raise ValueError()
		if (tests_root is None) or (tests_root == ""):
			raise ValueError()
		
		focal_dirname: str = path_split(focal_root)[1]
		tests_relpath: str = SystemPath(tests_root).relative_to(full_root).as_posix()
		self._proj_name = proj_name
		self._orig_full_root = full_root
		
		self._full_root: str = f"{self._path_prefix}/project"
		self._focal_root: str = f"{self._full_root}/{focal_dirname}"
		self._tests_root: str = f"{self._full_root}/{tests_relpath}"
		self._gentests_root: str = f"{self._full_root}/{self._gentests_dir}"
		self._envconfig_root: str = f"{self._full_root}/{self._envconfig_dir}"
		
		self._set_envconfig_entities()

		self._project_set = True
	
	
	def set_path_prefix(self, path_prefix: str):
		self._assert_inited()

		pathpref_found: Match[str] = reg_search(self._LINUXPATH_PATT, path_prefix)
		if pathpref_found.group("path_prefix") is None:
			raise ValueError()
		
		path_prefix_strpd: str = path_prefix.rstrip("/")

		self._full_root = self._change_prefix_of_path(
			path_prefix_strpd,
			self._full_root,
		)
		self._focal_root = self._change_prefix_of_path(
			path_prefix_strpd,
			self._focal_root,
		)
		self._tests_root = self._change_prefix_of_path(
			path_prefix_strpd,
			self._tests_root,
		)
		self._gentests_root = self._change_prefix_of_path(
			path_prefix_strpd,
			self._gentests_root,
		)
		self._envconfig_root = self._change_prefix_of_path(
			path_prefix_strpd,
			self._envconfig_root,
		)

		self._change_prefix_envc_entities(path_prefix_strpd)

		self._path_prefix = path_prefix_strpd
	
	
	def build_image(
			self,
			wants_dockign: bool = True
	) -> DockerImage:
		self._assert_inited()

		python_tag: str = self._get_python_version()
		ext_deps: List[str] = self._get_ext_deps()
		
		# Initializing a new Dockerfile
		self._dockf_builder.new_dockerfile()
		self._dockf_builder.set_base_image(f"python:{python_tag}")
		
		# Installing BaSH
		self._dockf_builder.add_shellcmd("apt-get update && apt-get install -y bash"
		                                 " && rm -rf /var/lib/apt/lists/*")
		
		# Setting the version of the Python interpreter to be used
		py_version: str = reg_search(self._PYVERS_PATT, python_tag).group()
		self._dockf_builder.set_envvar("PYTHON_VERSION", py_version)
		
		# Create the path prefix and the tools root
		self._dockf_builder.add_copy(["."], f"{self._full_root}")
		
		# Copy the linting tools
		self._dockf_builder.add_copy(
			[self._linttools_dir],
			f"{self._path_prefix}/tools/{self._linttools_dir}/"
		)
		# Copy of the coverage tools
		self._dockf_builder.add_copy(
			[self._covtools_dir],
			f"{self._path_prefix}/tools/{self._covtools_dir}/"
		)
		# Removal of duplicate linting and coverage directories
		self._dockf_builder.add_shellcmd(f"rm -rf {self._full_root}/{self._linttools_dir} "
		                                 f"{self._full_root}/{self._covtools_dir}")
		
		# Copy the Env-Config Project Root Path outside the main project
		self._dockf_builder.add_copy(
			[self._envconfig_dir],
			f"{self._path_prefix}/{self._envconfig_dir}/"
		)
		# Removes the Env-Config Project Root Path from within the Full Project Root Path of the target environment
		self._dockf_builder.add_shellcmd(f"rm -rf {self._full_root}/{self._envconfig_dir}")
		
		# Add the path prefix and the full project root path to PYTHONPATH\
        # to ensure the tools run correctly
		self._dockf_builder.set_envvar(
			"PYTHONPATH",
		    f"{self._path_prefix}:{self._full_root}"
		)
		
		# Configuring local environment variables
		self._configure_local_envvars()
		
		# Installing the `yes` command (used for silent installations)
		self._dockf_builder.add_shellcmd("apt-get update && apt install -y coreutils"
		                                 " && apt-get clean"
		                                 " && rm -rf /var/lib/apt/lists/*")

		# Upgrading PIP
		self._dockf_builder.add_shellcmd("python -m pip install --upgrade pip")
		
		# Configuring dependency installation
		self._configure_deps_install(ext_deps)
		
		self._dockf_builder.begin_cmds_tran()
		# Install `coverage.py`
		self._dockf_builder.add_shellcmd_step(f'pip install coverage=="{self._ap__covpy_version()}"')
		# Installing `pylint`
		self._dockf_builder.add_shellcmd_step(f'pip install pylint=="{self._ap__pylint_version()}"')
		self._dockf_builder.commit_cmds_tran()
		
		# Installation of additional software specified
		# by the descendants of this abstract class
		self._p__install_extra_softws(self._dockf_builder)
		
		# Set the current directory to the root of the tools directory
		self._dockf_builder.add_workdir(f"{self._path_prefix}/tools")
		
		# Set the main process of the target environment\
		self._dockf_builder.set_entrypoint("sleep infinity")
		
		dockerfile_path: str = path_join(self._orig_full_root, self._dockf_fname)
		self._dockf_builder.build_dockerfile(dockerfile_path)
		
		# Copy the tools directories into the build context
		linttools_path: SystemPath = SystemPath(self._tools_root, self._linttools_dir)
		covtools_path: SystemPath = SystemPath(self._tools_root, self._covtools_dir)
		self._copy_tool_subroot_infullroot(str(linttools_path))
		self._copy_tool_subroot_infullroot(str(covtools_path))
		
		# Replace any existing .dockerignore file before building
		# the target environment
		dockign_path: str = path_join(self._orig_full_root, ".dockerignore")
		dockign_saved_path: str = path_join(self._orig_full_root, ".dockerignore.saved")
		if os_fdexists(dockign_path):
			os_rename(dockign_path, dockign_saved_path)
			
		if wants_dockign:
			with open(dockign_path, "w") as fdocki:
				fdocki.writelines(f"./{self._dockf_fname}")
				fdocki.flush()
		
		# Building the focal environment image
		proj_image: DockerImage = self._docker.images.build(
			path=self._orig_full_root,
			dockerfile=self._dockf_fname,
			tag=f"{self._tag_prefix}_{self._proj_name}",
			rm=True, forcerm=True, nocache=True,
			pull=False
		)[0]
		self._cache_cner.clean_buildcache()
		
		# Re-apply any .dockerignore file saved after the build of the target environment
		if os_fdexists(dockign_saved_path):
			os_rename(dockign_saved_path, dockign_path)
		
		# Removing the tool directories copied into the Full Project Root Path
        # to include them in the build context
		os_dremove(
			path_join(self._orig_full_root, self._linttools_dir)
		)
		os_dremove(
			path_join(self._orig_full_root, self._covtools_dir)
		)

		return proj_image
	
	
	##	============================================================
	##						ABSTRACT METHODS
	##	============================================================
	
	
	@abstractmethod
	def _ap__pylint_version(self) -> str:
		"""
			Returns the version of the `pylint` software to be installed
            
            Returns
            -------
                str
                    A string representing the version of `pylint` to be installed
		"""
		pass
	
	
	@abstractmethod
	def _ap__covpy_version(self) -> str:
		"""
			Returns the version of `coverage.py` to be installed
            
            Returns
            -------
                str
                    A string representing the version of `coverage.py` to be installed
		"""
		pass
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================
	
	
	def _p__install_extra_softws(self, dockf_builder: ATransactDockfBuilder):
		"""
			Adds instructions to the Dockerfile to install the additional software
            specified by the subclasses of this abstract class.
            
            The default implementation is empty.
            
            The following environment variables are already available in the provided Dockerfile builder:
			
				- `PYTHON_VERSION`: The version of the Python interpreter present in the focal environment
                - `FULL_ROOT`: The Full Project Root Path within the focal environment
                - `FOCAL_ROOT`: The Focal Project Root Path within the focal environment
				- `TESTS_ROOT`: The Tests Project Root Path within the focal environment
                - `GENTESTS_ROOT`: The Gen-tests Project Root Path within the focal environment
                - `LINTTOOLS_DIR`: The name of the folder containing the linting verification tools
				
			ASSUMPTION: It is assumed that only additions are made
            and no changes are made to the contents of the provided Dockerfile builder.
			The following operations are therefore prohibited:
                
                - `.new_dockerfile(...)` and `.set_base_image(...)`
                - `.set_global_args(...)` and `.set_entrypoint(...)`
			
			Parameters
            ----------
                dockf_builder: ATransactDockfBuilder
                    An `ATransactDockfBuilder` object representing the Dockerfile builder
                    to which instructions for installing additional software should be added
		"""
		return
	
	
	def _assert_inited(self):
		"""
			Asserts that this _ABaseFocalEnvConfigurator has been fully initialized by:
            setting:
                - The context data for the focal project from which to generate the Docker image
                - The Python interpreter version to use as the default

            Raises
            ------
				FocalProjectNotSetError
                    If a focal project is not set before calling this operation

                DefaultPythonVersionNotSetError
                    If no default tag has been set for the "python" image
                    before calling this operation
		"""
		if not self._project_set:
			raise FocalProjectNotSetError()
		if not self._def_pyvers_set:
			raise DefaultPythonVersionNotSetError()
	
	
	def _change_prefix_of_path(
			self,
			new_path_prefix: str,
			path_tochange: str
	) -> str:
		"""
			Changes the path prefix to a path provided as an argument

            Parameters
            ----------
                new_path_prefix: str
                    A string containing the new path prefix to use when modifying the path

                path_tochange: str
					A string containing the path whose path prefix is to be changed

            Returns
            -------
                str
                    A string containing the given path with the updated path prefix
		"""
		return PosixPath(
			new_path_prefix,
			PosixPath(path_tochange).relative_to(self._path_prefix)
		).as_posix()
	
	
	def _change_prefix_envc_entities(
			self,
			new_path_prefix: str,
	):
		"""
			Change the path prefix for all paths associated with the container that correspond to
            the files in the Env-Config Project Root Path

            Parameters
            ----------
                new_path_prefix: str
                    A string containing the new path prefix to be used to modify the paths
		"""
		if os_fdexists(self._ext_deps_path):
			if self._prescr_path != "":
				self._prescr_path = self._change_prefix_of_path(
					new_path_prefix,
					self._prescr_path,
				)
			if self._postscr_path != "":
				self._postscr_path = self._change_prefix_of_path(
					new_path_prefix,
					self._postscr_path,
				)

		if self._prescrpy_path != "":
			self._prescrpy_path = self._change_prefix_of_path(
				new_path_prefix,
				self._prescrpy_path,
			)
			
		if self._postscrpy_path != "":
			self._postscrpy_path = self._change_prefix_of_path(
				new_path_prefix,
				self._postscrpy_path,
			)

			
	def _set_envconfig_entities(self):
		"""
			Set the paths for the elements in the Env-config Project Root Path
            (based on their existence)
		"""
		orig_envconfig_root = path_join(self._orig_full_root, self._envconfig_dir)
		
		self._py_vers_path = self._set_envc_entity_ifexists(
			orig_envconfig_root,
			self._py_vers_fname,
		)
		
		self._py_deps_path = self._set_envc_entity_ifexists(
			orig_envconfig_root,
			self._py_deps_fname,
		)
		self._ext_deps_path = self._set_envc_entity_ifexists(
			orig_envconfig_root,
			self._ext_deps_fname,
		)
		
		if self._ext_deps_path != "":
			self._prescr_path = self._set_envc_entity_ifexists(
				orig_envconfig_root,
				self._prescr_fname,
				container=True
			)

			self._postscr_path = self._set_envc_entity_ifexists(
				orig_envconfig_root,
				self._postscr_fname,
				container=True
			)
			
		self._prescrpy_path = self._set_envc_entity_ifexists(
			orig_envconfig_root,
			self._prescrpy_fname,
			container=True
		)
			
		self._postscrpy_path = self._set_envc_entity_ifexists(
			orig_envconfig_root,
			self._postscrpy_fname,
			container=True
		)
		
		
	def _set_envc_entity_ifexists(
			self,
			envconfig_root: str,
			entity_fname: str,
			container: bool = False
	) -> str:
		"""
			Set the value of a file in the Env-config Project Root Path, to be used
            within the target environment, if it actually exists

            Parameters
            ----------
				envconfig_root: str
                    A string containing the actual Env-Config Project Root Path
            
                entity_fname: str
                    A string containing the name of the file whose path is to be set relative
                    to the focal environment
					
				container: bool
                    Optional. Default = `False`. A boolean indicating whether the path to be
                    returned is relative to the container.
                    If this flag is `False`, the returned path is the actual path
                    of the provided Env-Config Project Root Path object

			Returns
            -------
                str
                    A string containing the path (relative to the container) of the given file
		"""
		orig_entity_path: str = path_join(envconfig_root, entity_fname)
		if not os_fdexists(orig_entity_path):
			return ""
		else:
			if container:
				return f"{self._path_prefix}/{self._envconfig_dir}/{entity_fname}"
			else:
				return orig_entity_path
		
		
	def _get_python_version(self) -> str:
		"""
			Returns the "python" image tag to be used for the focal environment

            Returns
            -------
                str
                    A string containing the "python" image tag to be used
                    for creating the focal environment
		"""
		python_vers: str
		if self._py_vers_path != "":
			with open(self._py_vers_path, "r") as fp:
				python_vers = fp.read().strip("\n\t ")
		else:
			python_vers = self._def_pyvers
		return python_vers
	
	
	def _get_py_deps(self) -> List[Dict[str, str]]:
		"""
			Reads Python dependencies from the file, relative to the specified target project.

            Returns
            -------
                List[Dict[str, str]]
                    A list of dictionaries containing one entry for each Python dependency to be installed.
					Each dictionary contains:
					
                        - "r": The dependency or dependencies to be installed with `pip` (if there is more than one, separate them with spaces)
                        - Every other key is a flag for the `pip` command (and any value, or None)
		"""
		py_deps: List[Dict[str, str]]
		if self._py_deps_path != "":
			with open(self._py_deps_path, "r") as fp:
				py_deps = self._json_dec.decode(fp.read())
			return py_deps
		return list()


	def _get_ext_deps(self) -> List[str]:
		"""
			Reads external dependencies from the file, relative to the specified focal project

            Returns
            -------
				List[str]
                    A list of strings containing one element for each external dependency to be installed.
                    Each external dependency is identified by the name of the package to be installed via `apt-get install`
		"""
		ext_deps: List[str] = []
		if self._ext_deps_path != "":
			with open(self._ext_deps_path, "r") as fp:
				ext_deps = fp.readlines()
			ext_deps = list(map(lambda x: x.strip("\n\t "), ext_deps))
		return ext_deps


	def _configure_local_envvars(self):
		"""
			Configure the Dockerfile builder to define local environment variables in the images
            that will be built later
		"""
		self._dockf_builder.set_envvar(
			"PATH",
		    "$HOME/.local/bin:$HOME/bin:$PATH"
		)
		self._dockf_builder.set_envvar("FULL_ROOT", self._full_root)
		self._dockf_builder.set_envvar("FOCAL_ROOT", self._focal_root)
		self._dockf_builder.set_envvar("TESTS_ROOT", self._tests_root)
		self._dockf_builder.set_envvar("GENTESTS_ROOT", self._gentests_root)
		self._dockf_builder.set_envvar("LINTTOOLS_DIRNAME", self._linttools_dir)
		self._dockf_builder.set_envvar("COVTOOLS_DIRNAME", self._covtools_dir)
		self._dockf_builder.set_envvar("CONTTOOLS_ROOT", f"{self._path_prefix}/tools")


	def _configure_deps_install(
			self,
			ext_deps: List[str],
	):
		"""
			Configure the Dockerfile builder to install project dependencies
            in the images that will be built later

            Parameters
            ----------
				ext_deps: List[str]
                    A list of strings containing one entry for each external dependency to be installed.
                    Each external dependency is identified by the name of the package to be installed via `apt-get install`
		"""
		# Esecuzione dello script Pre-installazione delle dipendenze esterne
		if os_fdexists(self._ext_deps_path):
			if self._prescr_path != "":
				self._dockf_builder.add_shellcmd(
					f'chmod a+x {self._prescr_path} && '
					f'/bin/bash {self._prescr_path}'
				)

		# Installazione delle dipendenze esterne
		if os_fdexists(self._ext_deps_path):
			self._dockf_builder.begin_cmds_tran()
			self._dockf_builder.add_shellcmd_step("apt-get update")
		for ext_dep in ext_deps:
			self._dockf_builder.add_shellcmd_step(f"apt-get install -y {ext_dep}")
		if os_fdexists(self._ext_deps_path):
			self._dockf_builder.add_shellcmd_step("apt-get clean")
			self._dockf_builder.add_shellcmd_step("rm -rf /var/lib/apt/lists/*")
			self._dockf_builder.commit_cmds_tran()

		# Esecuzione dello script Post-installazione delle dipendenze esterne
		if os_fdexists(self._ext_deps_path):
			if self._postscr_path != "":
				self._dockf_builder.add_shellcmd(
					f'chmod a+x {self._postscr_path} && '
					f'/bin/bash {self._postscr_path}'
				)
				
		# Esecuzione dello script Pre-installazione delle dipendenze Python
		if self._prescrpy_path != "":
			self._dockf_builder.add_shellcmd(
				f'chmod a+x {self._prescrpy_path} && '
				f'/bin/bash {self._prescrpy_path}'
			)

		# Installazione delle dipendenze (packages) Python
		py_deps: List[Dict[str, str]] = self._get_py_deps()
		py_packs: str
		pip_flags: str
		if len(py_deps) > 0:
			self._dockf_builder.begin_cmds_tran()
		for pydep_dict in py_deps:
			pip_flags = ""
			py_packs = pydep_dict.pop("r")
			for flag, value in pydep_dict.items():
				pip_flags += f"{flag}"
				if value is not None:
					pip_flags += f" {value}"
					
			self._dockf_builder.add_shellcmd_step(
				f"yes | python -m pip install --no-cache-dir -q -q -q {pip_flags} {py_packs}"
			)
		if len(py_deps) > 0:
			self._dockf_builder.commit_cmds_tran()
			
		# Esecuzione dello script Post-installazione delle dipendenze Python
		if self._postscrpy_path != "":
			self._dockf_builder.add_shellcmd(
				f'chmod a+x {self._postscrpy_path} && '
				f'/bin/bash {self._postscrpy_path}'
			)
		
		
	def _copy_tool_subroot_infullroot(self, tool_subroot: str):
		"""
			Copies the tools sub-root for the specified focal environment
            into the Full Project Root Path of the current focal project.
            This is used to enable `COPY` operations during the build
            of focal environment images.
			
			Parameters
            ----------
                tool_subroot: str
                    A string containing the sub-root to be copied into the
                    Full Project Root Path of the specified focal project
		"""
		tooldest_path: str = path_join(
			self._orig_full_root, path_split(tool_subroot)[1]
		)
		if os_fdexists(tooldest_path):
			os_dremove(tooldest_path)
		
		os_dcopy(
			tool_subroot,
			tooldest_path,
			dirs_exist_ok=False
		)
		
		
	@classmethod
	def _check_initargs(
			cls,
			tag_prefix: str,
			gentests_dir: str,
			envconfig_dir: str,
			dockerfile_fname: str,
			py_vers_fname: str,
			deps_files: Tuple[str, str, str, str, str, str],
			tools_root: str,
			linttools_dir: str,
			path_prefix: str
	):
		"""
			Checks the validity of the constructor arguments provided.
            
            If the check succeeds, this operation is equivalent to a no-op.
            
            Raises:
            ------
				ValueError
                    Occurs if:
                    
                        - The `tag_prefix` parameter is `None` or an empty string
                        - The `gentests_dir` parameter is `None` or an empty string
						- The `envconfig_dir` parameter is `None` or an empty string
                        - The `dockerfile_fname` parameter is `None` or an empty string
                        - The `py_vers_fname` parameter is `None` or an empty string
						- The `deps_files` parameter is `None`, is an empty tuple; or one of its elements is `None` or at least one is an empty string
                        - The `tools_root` parameter is `None`, is an empty string, or is an invalid path
						- The `linttools_dir` parameter is `None`, an empty string, or the directory does not exist in `tools_root`
                        - The `path_prefix` parameter is an empty string or an invalid Linux path
		"""
		if (
			(tag_prefix is None) or
			(gentests_dir is None) or
			(envconfig_dir is None) or
			(dockerfile_fname is None) or
			(py_vers_fname is None) or
			(deps_files is None) or
			(tools_root is None) or
			(linttools_dir is None) or
			(path_prefix is None)
		):
			raise ValueError()

		if (
			(tag_prefix == "") or
			(gentests_dir == "") or
			(envconfig_dir == "") or
			(dockerfile_fname == "") or
			(py_vers_fname == "") or
			(deps_files == tuple()) or
			(tools_root == "") or
			(path_prefix == "") or (reg_search(cls._LINUXPATH_PATT, path_prefix) is None)
		):
			raise ValueError()
		
		for dep_file in deps_files:
			if (
				(dep_file is None) or
				(dep_file == "")
			):
				raise ValueError()