from typing import Set
from abc import abstractmethod
from .. import IPtsuiteCacheAccessor

# ============ Path Utilities ============ #
from os.path import splitext as path_split_ext
# ======================================== #
# ============== OS Utilities ============== #
from os.path import isdir as os_isdir
# ========================================== #

from ..exceptions import (
	CacheFileTypeError,
	ProjectSpaceNotExistsError,
	EntryAlreadyExistsError,
	EntryNotExistsError
)



class _ABasePtsuiteCacheAccessor(IPtsuiteCacheAccessor):
	"""
		Represents a base `IPtsuiteCacheAccessor`, meaning it contains the logic common to all
		`IPtsuiteCacheAccessor` instances.
        
        The cache implementation technology is specified by the subclasses of this abstract class.
        The purpose of the cache is specified by the subclasses of this abstract class.
	"""
	
	def __init__(self, cache_path: str):
		"""
			Creates a new _ABasePtsuiteCacheAccessor and associates it with the
            cache that will be used
            
            Parameters
            ----------
                cache_path: str
                    A string representing the path to the caching file that
                    will be used
					
			Raises
            ------
                ValueError
                    Occurs if:
                        
                        - The `cache_path` parameter is `None`
                        - The `cache_path` parameter is an empty string
		"""
		if (cache_path is None) or (cache_path == ""):
			raise ValueError()
		
		self._cache_path: str = cache_path.strip(" \t\n")
		self._proj_spaces: Set[str] = set()
	
	
	def close(self):
		return
	
	
	def create_projspace(self, proj_name: str):
		if (proj_name is None) or (proj_name == ""):
			raise ValueError()
		
		self._ap__create_projspace_spec(proj_name)
		
		self._proj_spaces.add(proj_name)
	
		
	def register_ptsuite(
			self,
			proj_name: str,
			module_name: str, entity: str, model: str, try_num: int,
			ptsuite_code: str
	):
		if ((proj_name is None) or (proj_name == "") or
			(module_name is None) or (module_name == "") or
			(entity is None) or (entity == "") or
			(model is None) or (model == "") or
			(ptsuite_code is None)
		):
			raise ValueError()
		if try_num < 0:
			raise ValueError()
		
		if proj_name not in self._proj_spaces:
			raise ProjectSpaceNotExistsError()
		
		if self.does_ptsuite_exists(proj_name, module_name, entity, model, try_num):
			raise EntryAlreadyExistsError()
		
		self._ap__register_ptsuite_spec(
			proj_name,
			module_name, entity, model, try_num,
			ptsuite_code
		)
		
	
	def get_ptsuite(
			self,
			proj_name: str,
			module_name: str, entity: str, model: str, try_num: int
	) -> str:
		if ((proj_name is None) or (proj_name == "") or
			(module_name is None) or (module_name == "") or
			(entity is None) or (entity == "") or
			(model is None) or (model == "")
		):
			raise ValueError()
		if try_num < 0:
			raise ValueError()
		
		if proj_name not in self._proj_spaces:
			raise ProjectSpaceNotExistsError()
		
		if not self.does_ptsuite_exists(proj_name, module_name, entity, model, try_num):
			raise EntryNotExistsError()
		
		return self._ap__get_ptsuite_spec(
			proj_name, module_name, entity, model, try_num
		)
	
	
	def _pf__get_cache_path(self) -> str:
		"""
			Returns the path containing the caching file
            
            Returns
            -------
                str
                    A string representing the path containing the caching file
                    to be used
		"""
		return self._cache_path
	
	
	def _p__file_extension(self) -> str:
		"""
			Returns the extension required for the caching file
            
            Implementation of this method is optional if the file type
            does not require a specific extension
            
            Returns
            -------
				str
                    A string, in lowercase and without a period, containing the extension
                    that the caching file must have.
		"""
		return ""
	
	
	def _P__objinit(self):
		"""
			Checks/ensures the invariants of the newly constructed object
            
            Raises
            ------
				CacheFileTypeError
                    Occurs if the path does not represent a caching file compatible
                    with the implementation technology specified by the descendants of this
                    abstract class.
                    
                OSError
                    Occurs if the `cache_path` parameter points to a directory
		"""
		extens: str = self._p__file_extension()
		if extens != "":
			if path_split_ext(self._cache_path)[1].lower() != f".{extens}":
				raise CacheFileTypeError()
		
		if os_isdir(self._cache_path):
			raise OSError()
		
		just_created: bool = False
		try:
			open(self._cache_path, "r").close()
		except FileNotFoundError:
			self._ap__create_new_cache(self._cache_path)
			just_created = True
		
		if not just_created:
			self._ap__assert_cache_type(self._cache_path)
			self._proj_spaces = self._ap__read_project_spaces()
	
	
	#	============================================================
	#						ABSTRACT METHODS
	#	============================================================
	
	
	@abstractmethod
	def _ap__read_project_spaces(self) -> Set[str]:
		"""
			Reads the project spaces contained in the associated cache
            
            Returns
            -------
                Set[str]
                    A set of strings containing the names of the project spaces
                    that make up the associated cache
		"""
		pass
	
	
	@abstractmethod
	def _ap__create_new_cache(self, cache_path: str):
		"""
			Creates a new cache file at the specified path.
			
			This method ensures that the associated cache
            has already been initialized and is ready for use
            
            Parameters
            ----------
                cache_path: str
                    A string representing the path of the cache to be
                    created
		"""
		pass
	
	
	@abstractmethod
	def _ap__assert_cache_type(self, cache_path: str):
		"""
			Checks whether the cache provided as an argument is compatible with the implementation technology
            of the cache represented by the subclasses of this abstract class.
            
            If the check succeeds, this operation is equivalent to a no-op.
            
            The following are guaranteed within this method:
			
				- That the `cache_path` parameter is not `None`
                - That the `cache_path` parameter is not an empty string
                - That the file at the `cache_path` exists
                - That the `cache_path` parameter points to a file with the correct extension
			
			Parameters
            ----------
                cache_path: str
                    A string representing the path containing the caching file
                    to be verified
		"""
		pass
	
	
	@abstractmethod
	def _ap__create_projspace_spec(self, proj_name: str):
		"""
			Reserves the storage space required for the partial test suites
            of the specified project.
            
            If the storage space already exists, this operation is equivalent to a no-op.
			
			The following are guaranteed within this method:
            
                - That the `proj_name` parameter is not `None`
                - That the `proj_name` parameter is not an empty string
            
            Parameters
            ----------
				proj_name: str
                    A string containing the name of the new project for which to reserve
                    storage space in the represented cache
                    
            Raises
            ------
                ProjectSpaceReservationError
                    Occurs if an error occurs while reserving storage space
		"""
		pass
	
	
	@abstractmethod
	def _ap__register_ptsuite_spec(self,
	        proj_name: str,
			module_name: str, entity: str, model: str, try_num: int,
			ptsuite_code: str
	):
		"""
			Records a new attempt to generate a partial test suite
            in the represented cache
            
            The following are guaranteed within this method:
                
                - That `try_num >= 0`
                - That no string parameter is `None`
				- That no string parameter is empty (except `ptsuite_code`)
                - That the storage space for the `proj_name` project exists
                - That no attempt corresponding to the quintuple
                  (`proj_name`, `module_name`, `entity`, `model`, `try_num`) already exists
		
			Parameters
            ----------
                proj_name: str
                    A string containing the name of the project for which to record the attempt
                    to generate the partial test suite
                
                module_name: str
					A string containing the name of the focal module for which
                    the partial test suite is being cached
                    
                entity: str
                    A string containing the name of the code entity to which
                    the partial test suite being cached belongs
					
				model: str
                    A string representing the name of the LLM that generated the attempt
                    to be cached
                    
                try_num: int
                    An integer indicating the number of the generation attempt corresponding to
                    this “version” of the partial test suite to be cached
					
				ptsuite_code: str
                    A string containing the code of the partial test suite, generated by the LLM attempt,
                    to be stored in the cache
		"""
		pass
	
	
	@abstractmethod
	def _ap__get_ptsuite_spec(
			self,
	        proj_name: str,
			module_name: str, entity: str, model: str, try_num: int
	) -> str:
		"""
			Returns the attempt to generate a partial test suite, in the represented cache,
            associated with the following characteristics.
            
            The following are guaranteed within this method:
            
                - That `try_num >= 0`
                - That no string parameter is `None` or an empty string
				- That the storage space for the `proj_name` project exists
                - That a run exists corresponding to the quintuple
                  (`proj_name`, `module_name`, `entity`, `model`, `try_num`)
                  
            Parameters
            ----------
				proj_name: str
                    A string containing the name of the project for which the attempt
                    to generate the partial test suite is being sought
                
                module_name: str
                    A string containing the name of the target module for which
                    the partial test suite is being cached
					
				entity: str
                    A string containing the name of the code entity to which
                    the partial test suite being cached belongs
                    
                model: str
                    A string representing the name of the LLM from which
                    the attempt in the cache was generated
					
				try_num: int
                    An integer indicating the number of the generation attempt corresponding to
                    the “version” of the partial test suite being searched for
        
            Returns
            -------
				str
                    A string containing the code of the partial test suite for the attempt being searched for
                    in the cache
		"""
		pass
	
	
	@abstractmethod
	def does_ptsuite_exists(
			self,
	        proj_name: str,
			module_name: str, entity: str, model: str, try_num: int
	) -> bool:
		pass
		
		
	#	============================================================
	#						PRIVATE METHODS
	#	============================================================


	def __enter__(self):
		return self


	def __exit__(self, exc_type: type, exc: Exception, traceback):
		self.close()