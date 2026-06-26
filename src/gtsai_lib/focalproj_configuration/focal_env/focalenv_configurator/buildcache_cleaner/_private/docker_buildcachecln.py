from .i_buildcache_cleaner import IBuildCacheCleaner

# ============== OS Utilities ============== #
from os import environ as os_envvar
# ========================================== #
# ============== Docker SDK Utilities =============== #
from docker import (
	from_env as docker_getclient,
	DockerClient
)
# =================================================== #



class DockerBuildCacheCleaner(IBuildCacheCleaner):
	"""
		Represents an `IBuildCacheCleaner` for the Docker "Container Manager"
	"""
	
	def __init__(self):
		"""
			Creates a new DockerBuildCacheCleaner
		"""
		self._docker: DockerClient
		try:
			docker_host: str = os_envvar["DOCKER_HOST"]
			self._docker = DockerClient(base_url=docker_host)
		except KeyError:
			self._docker = docker_getclient()
	
	
	def clean_buildcache(self):
		self._docker.images.prune_builds()


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================