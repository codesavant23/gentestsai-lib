from enum import Enum as PythonEnumerator



class EContainerManager(PythonEnumerator):
	"""
		Rperesents a "Container Manager" from which you can retrieve the cleaner
        for the build cache in GenTestsAI
	"""
	DOCKER = 0,
	PODMAN_GE400 = 1
	PODMAN_LT400 = 2