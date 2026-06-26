from .i_buildcache_cleaner import IBuildCacheCleaner

from subprocess import run as subp_run



class PodmanGe400BuildCacheCleaner(IBuildCacheCleaner):
	"""
		Represents `IBuildCacheCleaner` for the Podman "Container Manager"
        whose version is ">=4.0"
	"""
	
	def __init__(self):
		"""
			Creates a new PodmanGe40BuildCacheCleaner
		"""
		pass
	
	
	def clean_buildcache(self):
		subp_run(["podman", "builder", "prune"])


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================