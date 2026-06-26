from typing import Dict

from regex import (
	Pattern,
	compile as create_pattern,
	escape as reg_escape,
)

from ..exceptions import (
	TemplateNotSetError,
	InvalidPlaceholderError,
	IncompletePromptError
)



class PromptBuilder:
	"""
		Represents an object capable of constructing a full prompt given a template in which to replace the placeholders.

		The placeholders accepted by this full prompt builder are identified by enclosing the placeholder name
		between two delimiters: one at the beginning of the name and one at the end.

		By default, this object uses the following delimiters:
            - Start: `{@`
            - End: `@}`

        e.g.    Placeholder in the template with the default delimiters:
        Place_Holder1    ----identified-by---->    {@Place_Holder1@}
	"""

	def __init__(
			self,
			template_prompt: str = None,
			init_del: str="{@",
			end_del: str="@}"
	):
		"""
			Creates a new PromptBuilder by binding it to a specific prompt template

            Parameters
            ----------
				template_prompt: str
                    Optional. Default = `None`. A string containing the prompt template to use as a basis.
                    If the prompt template is not provided now, it must be provided later,
                    using the `.` method

                init_del: str
					Optional. Default = `{@`. A string containing the opening delimiter to recognize
                    placeholders in the template

                end_del: str
                    Optional. Default = `{@`. A string containing the closing delimiter to recognize
                    placeholders in the template
		"""
		self._idel: str = init_del
		self._edel: str = end_del
		self._templ: str = template_prompt

		self._placehs: Dict[str, str] = None
		if self._templ is not None:
			self._placehs = self._init_placehs_dict(template_prompt, init_del, end_del)


	def set_template_prompt(self, template_prompt: str):
		"""
			Set a new prompt template to create the full prompt from,
            unlinking any previously set template
			
			Raises:
            ------
                ValueError
                    Occurs if:
                    
                        - The `template_prompt` parameter is `None`
                        - The `template_prompt` parameter is an empty string
		"""
		if (template_prompt is None) or (template_prompt == ""):
			raise ValueError()
		
		self._templ = template_prompt
		
		if self._placehs is not None:
			del self._placehs
		self._placehs = self._init_placehs_dict(
			template_prompt, self._idel, self._edel
		)


	def does_placeh_exists(
			self,
			placeh_name: str
	) -> bool:
		"""
			Checks whether the placeholder with the specified name exists in the associated template and can be used

            Parameters
            ----------
                placeh_name: str
                    A string containing the name of the placeholder to check for existence

            Returns
			-------
                bool
                    A boolean indicating whether the placeholder named `placeh_name` exists
                    
            Raises
            ------
                TemplateNotSetError
                    Occurs if no prompt template has been set yet
		"""
		if self._templ is None:
			raise TemplateNotSetError()
		
		if placeh_name in self._placehs:
			return True
		else:
			return False
	
	
	def unset_placeholders(self):
		"""
			Removes the value set for each placeholder
            
            Raises
            ------
                TemplateNotSetError
                    Occurs if no prompt template has been set yet
		"""
		if self._templ is None:
			raise TemplateNotSetError()
		
		for key in self._placehs.keys():
			self._placehs[key] = None
		

	def set_placeholder(
			self,
			name: str,
			value: str
	):
		"""
			Replaces the specified placeholder in the prompt template associated with this PromptBuilder with the chosen value

            Parameters
            ----------
				name: str
                    A string identifying the name of the placeholder to be replaced

                value: str
                    A string identifying the value with which to replace the specified placeholder

			Raises
            ------
                TemplateNotSetError
                    Occurs if no prompt template has been set yet
                    
                InvalidPlaceholderError
                    If the placeholder named `name` does not exist in the prompt template associated with this prompt builder
		"""
		if self._templ is None:
			raise TemplateNotSetError()
		if not self.does_placeh_exists(name):
			raise InvalidPlaceholderError()

		self._placehs[name] = value


	def build_prompt(self) -> str:
		"""
			Constructs the full prompt resulting from the substitutions made in the template.
            All placeholders must be replaced before calling this operation.

            Returns
            -------
                str
                    A string containing the full prompt resulting from the substitutions in the prompt template

			Raises
            ------
                TemplateNotSetError
                    Occurs if no prompt template has been set yet
            
                IncompletePrompt
                    If this operation is performed without first replacing all placeholders
                    in the prompt template
		"""
		if self._templ is None:
			raise TemplateNotSetError()
		
		for placeh, value in self._placehs.items():
			if value is None:
				raise IncompletePromptError()

		full_prompt: str = self._templ
		for placeh, value in self._placehs.items():
			full_prompt = full_prompt.replace(
				f"{self._idel}{placeh}{self._edel}",
				value
			)

		return full_prompt
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================
	
	
	@classmethod
	def _init_placehs_dict(
			cls,
			template_prompt: str,
			init_del: str,
			end_del: str
	) -> Dict[str, str]:
		placehs_dict: Dict[str, str] = dict()
		
		plach_patt: Pattern = create_pattern(
			fr"{reg_escape(init_del)}(?P<placeh_name>[A-Za-z0-9_]+){reg_escape(end_del)}"
		)
		for placeh_match in plach_patt.finditer(template_prompt):
			placehs_dict[placeh_match.group("placeh_name")] = None
			
		return placehs_dict