from .. import IPtsuiteCacheAccessor
from .e_cacheaccsor_type import ECacheAccessorType

from .._private._a_base_cacheaccsor import _ABasePtsuiteCacheAccessor
from .._private.sqlite3_cacheaccsor import Sqlite3CacheAccessor



class PtsuiteCacheAccessorFactory:
	"""
		Represents a factory for each `IPtsuiteCacheAccessor`
	"""
		
	
	@classmethod
	def create(
			cls,
			tech: ECacheAccessorType,
	        cache_path: str
	) -> IPtsuiteCacheAccessor:
		"""
			Instantiates a new cache accessor of the specified implementation technology
			
			Parameters
			----------
			    tech: ECacheAccessorType
			       An `ECacheAccessorType` value representing the required technology
			       for the `IPtsuiteCacheAccessor` object
			       
			    cache_path: str
			       A string representing the path containing the caching file
			       to be used
			       
			Returns
			-------
			    IPtsuiteCacheAccessor
			       An `IPtsuiteCacheAccessor` object that provides access to a cache
			       of the specified implementation technology
			       
			Raises
			------
			    ValueError
			       Occurs if:
			          
			          - The `cache_path` parameter is `None`
			          - The `cache_path` parameter is an empty string
			          
			    OSError
			       Occurs if the `cache_path` parameter points to a directory
			       
			    CacheFileTypeError
			       Occurs if the path does not represent a caching file compatible
			       with the required implementation technology
		"""
		obj: _ABasePtsuiteCacheAccessor
		match tech:
			case ECacheAccessorType.SQLITE3:
				obj = Sqlite3CacheAccessor(cache_path)
		
		obj._P__objinit()
		return obj
		
		
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================