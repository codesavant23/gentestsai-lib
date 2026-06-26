from typing import Tuple, Set
from ._a_base_cacheaccsor import _ABasePtsuiteCacheAccessor

# =========== SQLite3 Utilities ============ #
from sqlite3 import (
	connect as sql_connect,
	Connection as SqlConnection,
	Cursor as SqlConnectionCursor,
)
# ========================================== #

from ..exceptions import CacheFileTypeError



class Sqlite3CacheAccessor(_ABasePtsuiteCacheAccessor):
	"""
		Represents an `IPtsuiteCacheAccessor` that uses a local
		SQLite3 database as its cache
	"""
	
	def __init__(
			self,
			cache_path: str
	):
		"""
			Creates a new Sqlite3CacheAccessor by associating it with the path
            to the SQLite3 caching database to be used
            
            Parameters
            ----------
                cache_path: str
                    A string representing the path to the SQLite3 caching database
                    to be used
                    
            Raises
            ------
                ValueError
                    Occurs if:
                        
                        - The `cache_path` parameter is `None`
                        - The `cache_path` parameter is an empty string
		"""
		super().__init__(cache_path)
		
		self._conn: SqlConnection = sql_connect(cache_path)
		self._cursor: SqlConnectionCursor = self._conn.cursor()
	
	
	def close(self):
		self._cursor.close()
		self._conn.close()
	
	
	def does_ptsuite_exists(
			self,
			proj_name: str,
			module_name: str, entity: str, model: str, try_num: int
	) -> bool:
		row: Tuple[str, str, str, str, str]= self._query_db(
			proj_name, module_name, entity, model, try_num
		)

		return (row is not None)
	
	
	def _ap__create_new_cache(self, cache_path: str):
		open(cache_path, "w").close()
	
	
	def _ap__read_project_spaces(self) -> Set[str]:
		self._cursor.execute(f"""
			SELECT name FROM sqlite_master
			WHERE type='table';
		""")
		tables: Set[str] = {row[0] for row in self._cursor.fetchall()}
		return tables
	
	
	def _ap__create_projspace_spec(self, proj_name: str):
		self._cursor.execute(f"""
			CREATE TABLE IF NOT EXISTS "{proj_name}" (
				`module_name` TEXT NOT NULL,
				`entity` TEXT NOT NULL,
				`model` TEXT NOT NULL,
				`try_num` INTEGER NOT NULL,
				`ptsuite` TEXT NOT NULL,
				PRIMARY KEY (`module_name`, `entity`, `model`, `try_num`)
			)
		""")
		self._conn.commit()
	
	
	def _ap__register_ptsuite_spec(
			self,
			proj_name: str,
			module_name: str, entity: str, model: str, try_num: int,
			ptsuite_code: str
	):
		self._cursor.execute(f"""
			INSERT INTO {proj_name} (module_name, entity, model, try_num, ptsuite)
			VALUES (?, ?, ?, ?, ?);
		""",
		[module_name, entity, model, try_num, ptsuite_code])
		self._conn.commit()
	
	
	def _ap__get_ptsuite_spec(self, proj_name: str, module_name: str, entity: str, model: str, try_num: int) -> str:
		partial_tsuite: str = self._query_db(
			proj_name,
			module_name, entity, model, try_num
		)[4]
		return partial_tsuite
	
	
	def _ap__assert_cache_type(self, cache_path: str):
		header: bytes
		with open(cache_path, "rb") as fp:
			header = fp.read(16)
			
		if (header != b"SQLite format 3\x00") and (header != b""):
			raise CacheFileTypeError()


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================


	def _query_db(
			self,
			project_name: str,
			module_name: str,
			entity: str,
			model: str,
			try_num: int
	) -> Tuple[str, str, str, str, str]:
		self._cursor.execute(f"""
			SELECT * FROM `{project_name}`
			WHERE `module_name` = ?
			AND `entity` = ?
			AND `model` = ?
			AND `try_num` = ?
		""", [module_name, entity, model, try_num])

		return self._cursor.fetchone()