from abc import ABC, abstractmethod



class IPtsuiteCacheAccessor(ABC):
	"""
		Represents an object that provides access to a cache of partial test suites resulting
        from a process that uses Large Language Models.
        Each entry in the cache is an attempt to generate, using an LLM, a working partial test suite.
        
        Every `IPtsuiteCacheAccessor` supports Python's "Context Manager".
		
		The cache implementation technology is specified by the descendants of this interface.
	"""
	

	@abstractmethod
	def close(self):
		"""
			Releases the resources used by this cache accessor.
            This operation must be called at the end of the usage of this `IPtsuiteCacheAccessor`.
            If you use this object with the "Context Manager", then this
            operation is already guaranteed to be called.
			
			If there is nothing to release, this operation is equivalent to a no-op.
            
            The default implementation is empty
		"""
		pass


	@abstractmethod
	def create_projspace(self, proj_name: str):
		"""
			Reserves the storage space required for the partial test suites
            of the specified project.
            
            If the storage space already exists, this operation is equivalent to a no-op
            
            Parameters
            ----------
				proj_name: str
                    A string containing the name of the new project for which to reserve
                    storage space in the represented cache
                    
            Raises
            ------
				ValueError
                    Occurs if:
                        
                        - The `proj_name` parameter is `None`
                        - The `proj_name` parameter is an empty string
            
                ProjectSpaceReservationError
                    Occurs if an error occurs while reserving storage space
		"""
		pass
	
	
	@abstractmethod
	def register_ptsuite(
			self,
	        proj_name: str,
			module_name: str, entity: str, model: str, try_num: int,
			ptsuite_code: str
	):
		"""
			Caches a new attempt to generate a partial test suite
            in the specified cache
            
            Parameters
            ----------
                proj_name: str
                    A string containing the name of the project for which to cache
                    the attempt to generate the partial test suite
				
				module_name: str
                    A string containing the name of the target module for which
                    the partial test suite is being cached
                    
                entity: str
                    A string containing the name of the code entity to which
					the partial test suite being cached
                
                model: str
                    A string representing the name of the LLM from which the attempt
                    to be cached was generated
                    
                try_num: int
                    An integer indicating the number of the generation attempt corresponding to
					this "version" of the partial test suite that you want to cache
                
                ptsuite_code: str
                    A string containing the code of the partial test suite, produced by the LLM attempt,
                    to be cached
                    
			Raises
            ------
                ValueError
                    Occurs if:
					
						- At least one of `proj_name`, `module_name`, `entity`, `model`, and `ptsuite_code` is `None`
                        - At least one of `proj_name`, `module_name`, `entity`, or `model` is an empty string
                        - The `try_num` parameter is less than 0
			
				ProjectSpaceNotExistsError
                    Occurs if the storage space for `proj_name` does not exist
                    
                EntryAlreadyExistsError
                    Occurs if a production attempt associated with the given quintuple
                    (`proj_name`, `module_name`, `entity`, `model`, `try_num`) already exists
		"""
		pass
	
	
	@abstractmethod
	def does_ptsuite_exists(
			self,
	        proj_name: str,
			module_name: str, entity: str, model: str, try_num: int,
	) -> bool:
		"""
			Check whether a build attempt for a partial test suite exists
            in the associated cache with the following characteristics
            
            Parameters
            ----------
                proj_name: str
					A string containing the name of the project for which you are searching
                    for the partial test suite build attempt
                
                module_name: str
                    A string containing the name of the target module for which you are
                    caching the partial test suite
					
				entity: str
                    A string containing the name of the code entity to which
                    the partial test suite being cached belongs
                    
                model: str
                    A string representing the name of the LLM from which
                    the attempt in the cache was generated
					
				try_num: int
                    An integer indicating the number of the generation attempt corresponding to
                    the "version" of the partial test suite being searched for
                    
            Returns
            -------
                bool
                    A boolean indicating whether the attempt being searched for exists in the represented cache
		"""
		pass
	
	
	@abstractmethod
	def get_ptsuite(
			self,
	        proj_name: str,
			module_name: str, entity: str, model: str, try_num: int
	) -> str:
		"""
			Returns the attempt to generate a partial test suite, in the represented cache,
            associated with the following characteristics
            
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
                    the "version" of the partial test suite being searched for
		
			Returns
            -------
                str
                    A string containing the code of the partial test suite, of the attempt being searched for,
                    represented in the cache
                    
			Raises
            ------
                ValueError
                    Occurs if:
                    
                        - At least one of `proj_name`, `module_name`, `entity`, `model`, and `ptsuite_code` is `None`
						- At least one of `proj_name`, `module_name`, `entity`, `model`, and `ptsuite_code` is an empty string
                        - The `try_num` parameter is less than 0
            
                ProjectSpaceNotExistsError
                    Occurs if the storage space for `proj_name` does not exist
					
				EntryNotExistsError
                    Occurs if there is no partial test suite entry associated
                    with the given tuple (`proj_name`, `module_name`, `entity`, `model`, `try_num`)
		"""
		pass