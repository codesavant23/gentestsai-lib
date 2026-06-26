from typing import List

from shutil import which as os_which
from subprocess import check_output as subp_runout

from .e_contmanager import EContainerManager

from .._private.i_buildcache_cleaner import IBuildCacheCleaner
from .._private.docker_buildcachecln import DockerBuildCacheCleaner
from .._private.podmanlt400_buildcachecln import PodmanLt400BuildCacheCleaner
from .._private.podmange400_buildcachecln import PodmanGe400BuildCacheCleaner



class BuildCacheCleanerFactory:
	"""
		Represents a factory for each `IBuildCacheCleaner`
	"""
	
	
	@classmethod
	def obtain(cls, wanted_manager: EContainerManager=None) -> IBuildCacheCleaner:
		"""
			Instantiates a new build cache cleaner:
            
                - Either for the selected "Container Manager"
                - Or for the "Container Manager" used by the operating system
				
			If `wanted_manager` is not specified, and Docker and at least one "Container Manager"
            compatible with it (e.g., Podman) are available, this factory prioritizes Docker
            
            Parameters
            ----------
				wanted_manager: EContainerManager
                    Optional. Default = `None`. An `EContainerManager` value indicating the
                    "Container Manager" from which to obtain the build cache cleaner.
                    If no value is specified, a cleaner is obtained as specified
                    in the method description above
					
			Returns
			-------
                IBuildCacheCleaner
                    An `IBuildCacheCleaner` object that allows cleaning of the build
                    cache of the "Container Manager" selected for use
					
			Raises
            ------
                NotImplementedError
                    Occurs if the operating system uses a "Container Manager"
                    for which retrieval is not yet implemented
		"""
		obj: IBuildCacheCleaner
		
		match wanted_manager:
			case EContainerManager.DOCKER:
				obj = DockerBuildCacheCleaner()
			case EContainerManager.PODMAN_GE400:
				obj = PodmanLt400BuildCacheCleaner()
			case EContainerManager.PODMAN_LT400:
				obj = PodmanLt400BuildCacheCleaner()
		if wanted_manager is not None:
			return obj
		else:
			return cls._obtain_fromos()
		
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================


	@classmethod
	def _obtain_fromos(self):
		"""
			Ottiene il pulitore della cache di building in base al "Container Manager"
			utilizzato dal sistema operativo.
			
			Se Docker e almeno un "Container Manager" compatibile con esso (es. Podman)
			sono disponibili, si dà priorità a Docker
		"""
		obj: IBuildCacheCleaner
		
		cont_manager: str
		if os_which("docker") is not None:
			cont_manager = "docker"
		elif os_which("podman") is not None:
			cont_manager = "podman"
		else:
			raise NotImplementedError()
		
		match cont_manager:
			case "docker":
				obj = DockerBuildCacheCleaner()
			case "podman":
				version: List[str] = (subp_runout(['podman', 'version', '--format', '"{{.Client.Version}}"'], text=True).strip()
				                      .split("."))
				if int(version[0]) >= 4:
					obj = PodmanGe400BuildCacheCleaner()
				else:
					obj = PodmanLt400BuildCacheCleaner()
				
		return obj