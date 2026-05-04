# https://trafilatura.readthedocs.io/en/latest
# https://github.com/adbar/trafilatura

import trafilatura

from .base import CleanBase


class TrafilaturaCleaner(CleanBase):
	"""Trafilatura Cleaner"""

	def __init__(self, config: dict = {}, engine_ext: dict = {}):
		# default engine config
		config = {
			"engine": {
				"output_format": "markdown",  # output format
				"include_comments": False,  # include comments, default True
				"include_formatting": True,  # keep strong, em..., default False
			}
		}

		# important
		super().__init__("trafilatura", config, engine_ext)

	def logic(self, html: str, title: str = "") -> str:
		"""Convert HTML to Markdown using trafilatura
		:param html: original html string
		:param title: page title, defaults to ""
		:return: markdown string
		"""

		# Common configuration parameters by trafilatura:
		config = self.config["engine"]

		md = trafilatura.extract(
			html,
			output_format=config["output_format"],
			include_comments=config["include_comments"],
			include_formatting=config["include_formatting"],
		)
		return f"# {title}\n\n{md}"  # use markdownify
