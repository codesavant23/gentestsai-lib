from .i_buildcache_cleaner import IBuildCacheCleaner

from subprocess import (
	DEVNULL,
	run as subp_run
)
OS_DEVNULL = DEVNULL



class PodmanLt400BuildCacheCleaner(IBuildCacheCleaner):
	"""
		Represents an `IBuildCacheCleaner` for the Podman "Container Manager"
        whose version is "<4.0"
	"""
	
	def __init__(self):
		"""
			Creates a new PodmanLt40BuildCache
		"""
		pass
	
	
	def clean_buildcache(self):
		subp_run(
			"podman images -a --format \"{{.ID}} {{.Tag}}\" | "
			"awk '$2 == \"<none>\" {print $1}' | "
			"xargs -r podman rmi -f",
			shell=True,
			check=True,
			stdout=DEVNULL,
			stderr=DEVNULL
		)
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================