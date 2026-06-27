from typing import List, Tuple, Dict
from abc import abstractmethod
from .i_dockerfile_builder import IDockfBuilder

# ============ Path Utilities ============ #
from os.path import sep, altsep
# ======================================== #
# ============== JSON Utilities ============== #
from json import JSONEncoder
from json import dumps as json_dumps
# ============================================ #

from ...exceptions import BaseImageNotSetError


_PATH_SEPS: str = f"{sep}{altsep if altsep is not None else ''}"



class _ABaseDockfBuilder(IDockfBuilder):
	"""
		Represents a base `IDockfBuilder`, containing the control logic common
		to every `IDockfBuilder`
        
        The implementation technology for storing instructions is specified by the descendants
        of this abstract class
	"""
	
	def __init__(self):
		"""
			Creates a new _ABaseDockfBuilder
		"""
		self._bimage: str = None
		self._glob_args: Dict[str, str] = dict()
		self._entryp: List[str] = list()
		
		
	def new_dockerfile(self):
		self._bimage = None
		
		del self._glob_args
		self._glob_args = dict()
		
		self._entryp.clear()
		
		self._ap__new_dockerf_spec()
		
	
	def set_base_image(self, base_image: str):
		if (base_image is None) or (base_image == ""):
			raise ValueError()
		
		self._bimage = base_image
	
	
	def add_shell(self, shell_touse: str, args: List[str] = None):
		if (shell_touse == "") or (shell_touse is None):
			raise ValueError()
		operands: List[str] = list()
		operands.append(shell_touse)
		
		if args is not None:
			if len(args) == 0:
				raise ValueError()
			operands.extend(args)
		
		self._ap__add_instr("SHELL " + json_dumps(operands))
	
	
	def add_copy(self, sources: List[str], dest: str):
		if (sources is None) or (len(sources) == 0):
			raise ValueError()
		if (dest is None) or (dest == ""):
			raise ValueError()
		
		sources_snized: List[str] = list(map(
			lambda source: source.rstrip(_PATH_SEPS),
			sources
		))
		dest_snized: str = f"{dest.rstrip('/')}/"
		sources_str: str = " ".join(sources_snized)
		
		self._ap__add_instr(
			f"COPY {sources_str} {dest_snized}"
		)
	
	
	def set_global_args(self, global_args: Dict[str, str]):
		if global_args is None:
			raise ValueError()
		if len(global_args.keys()) == 0:
			raise ValueError()
		
		for key, value in global_args.items():
			self._glob_args[key] = value
	
	
	def set_envvar(self, var_name: str, value: str):
		if (var_name is None) or (var_name == ""):
			raise ValueError()
		if (value == ""):
			raise ValueError()
		
		self._ap__add_instr(f'ENV {var_name}={value}')
	
	
	def add_shellcmd(self, shell_cmd: str):
		if (shell_cmd is None) or (shell_cmd == ""):
			raise ValueError()
		
		self._ap__add_instr(f"RUN {shell_cmd}")
	
	
	def add_workdir(self, dest: str):
		if (dest is None) or (dest == ""):
			raise ValueError()
		
		self._ap__add_instr(
			f"WORKDIR {dest.rstrip('/')}/"
		)
	
	
	def set_entrypoint(
			self,
			entry_cmd: str,
			def_args: List[str] = None
	):
		if (entry_cmd is None) or (entry_cmd == ""):
			raise ValueError()
		
		if len(self._entryp) != 0:
			del self._entryp
			self._entryp = list()
		
		self._entryp.extend(entry_cmd.split(" "))
		if def_args is not None:
			self._entryp.extend(def_args)
		
		
	def build_dockerfile(
			self,
			dockf_path: str
	):
		if (dockf_path is None) or (dockf_path == ""):
			raise ValueError()
		if self._bimage is None:
			raise BaseImageNotSetError()
		
		global_args: str = ""
		for glob_arg, value in self._glob_args.items():
			global_args += f"ARG {glob_arg}={value}" + "\n"
		
		entryp: Tuple[str, str]  = self._get_entryp_parts()
		entryp_dockfinstr: str = ""
		if len(entryp) > 0:
			entryp_dockfinstr = f'ENTRYPOINT {entryp[0]}'+'\n'
			if entryp[1] != "[]":
				entryp_dockfinstr += f'CMD {entryp[1]}'
		
		dockf_content: str = self._build_content(
			f'FROM {self._bimage}',
			global_args,
			self._ap__get_dockf_body(),
			entryp_dockfinstr
		)
		
		with open(dockf_path, "w") as fdockf:
			fdockf.writelines(dockf_content)
			fdockf.flush()
	
	
	##	============================================================
	##						ABSTRACT METHODS
	##	============================================================
	
	
	@abstractmethod
	def _ap__new_dockerf_spec(self):
		"""
			Initializes the builder to create a new Dockerfile by clearing all instructions
            from the previously built Dockerfile.
			
			The following is guaranteed within this method:
                
                - That the base image has already been cleared
                - That the global arguments have already been cleared
                - That the entrypoint instruction has already been removed
		"""
		pass
	
	
	@abstractmethod
	def _ap__add_instr(self, instr: str):
		"""
			Adds the provided instruction to the Dockerfile that is being built incrementally
            
            Parameters
            ----------
                instr: str
                    A string containing the instruction to be added to the Dockerfile
                    that is being built
		"""
		pass
	
	
	@abstractmethod
	def _ap__get_dockf_body(self) -> str:
		"""
			Returns the main body of the current Dockerfile to write it to a file.
            The main body refers to all instructions that are not:
            
                - FROM
                - ARG
                - ENTRYPOINT or CMD
				
			Returns
            -------
                str
                    A string representing the main body of the Dockerfile that
                    contains its instructions
		"""
		pass
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================


	def _get_entryp_parts(self) -> Tuple[str, str]:
		"""
			Returns the components of the current `ENTRYPOINT`+`CMD` instruction,
            to be written in the Dockerfile
            
            Returns
            -------
				Tuple[str, str]
                    A tuple of 2 strings containing, if applicable:
                        
                        - [0]: The operand to be appended to the `ENTRYPOINT` directive (to be written in the Dockerfile)
						- [1]: The operand to be appended to the `CMD` directive (to be written in the Dockerfile)
                    
                    An empty tuple is returned if no entrypoint is set for the Dockerfile
		"""
		json_enc: JSONEncoder = JSONEncoder()
		
		if len(self._entryp) > 0:
			entryp_cmd: str = json_dumps(self._entryp[0:])
			entryp_args: str = json_enc.encode(self._entryp[1:])
			
			return (entryp_cmd, entryp_args)
		else:
			return tuple()
		
		
	@classmethod
	def _build_content(
			cls,
			base_image: str,
			glob_args: str,
			body: str,
			epcmd_instrs: str
	) -> str:
		"""
			Assemble the entire contents of the Dockerfile you want to create
            
            Parameters
            ----------
				base_image: str
                    A string containing the base image set for the Dockerfile
                    that will be built
                    
                glob_args: str
                    A string containing the `ARG` instructions that define the global arguments
                    of the Dockerfile that will be built
					
				body: str
                    A string containing the main body of the Dockerfile
            
                epcmd_instrs: str
                    A string containing any `ENTRYPOINT`+`CMD` instructions
                    to be inserted into the Dockerfile
		"""
		# Scrittura degli eventuali argomenti globali
		content: str = glob_args + "\n"
		content += "\n\n" if glob_args != "" else ""

		# Scrittura dell' immagine base
		content += base_image + "\n\n"
		
		# Scrittura delle istruzioni del Dockerfile
		content += (body + "\n\n")
		
		# Scrittura dell' eventuale coppia di istruzioni per l' entrypoint
		if epcmd_instrs != "":
			content += epcmd_instrs
			
		return content