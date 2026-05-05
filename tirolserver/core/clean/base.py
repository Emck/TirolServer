from abc import ABC, abstractmethod

from markdownify import markdownify as md

from tirolserver.utils import merge_dict_deep


class CleanBase(ABC):
	"""Clean Base Class"""

	def __init__(self, name: str, config: dict = {}, engine_ext: dict = {}):
		"""init cleaner
		:param name: engine name
		:param config: engine config
		:param engine_ext: engine extension config, defaults to {}
		"""

		self.title: str = None
		self.mdtext: str = ""
		self.config: dict = {
			"name": name,  # engine name
			"markdownify": {  # default internal markdownify config
				"heading_style": "ATX",  # use the '#' type title (instead of the underline type)
			},
		}
		merge_dict_deep(config.get("engine", {}), engine_ext)  # merage engine
		merge_dict_deep(self.config, config)  # merage config

	def html_to_markdown(self, html: str) -> str:
		"""internal convert html to markdown using markdownify
		:param html: original html string
		:return: markdown string
		"""

		# Common configuration parameters by markdownify:
		config = self.config["markdownify"]
		return md(
			html,
			heading_style=config["heading_style"],
		).strip()

	def run(self, html: str, title: str = "") -> tuple[str, str]:
		"""run clean HTML
		:param html: original html string
		:param title: page title, defaults to ""
		:return: engine name and markdown string
		"""

		self.mdtext = self.logic(html, title)
		return self.config["name"], self.mdtext

	@abstractmethod
	def logic(self, html: str, title: str = "") -> str:
		"""core logic, Convert HTML to Markdown
		:param html: original html string
		:param title: page title, defaults to ""
		:return: markdown string
		"""
		pass
