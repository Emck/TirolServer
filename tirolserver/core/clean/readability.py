# https://github.com/andreasvc/readability


from readability import Document

from .base import CleanBase


class ReadabilityCleaner(CleanBase):
	"""Readability Cleaner"""

	def __init__(self, config: dict = {}, engine_ext: dict = {}):
		# default engine config
		config = {
			"engine": {
				"min_text_length": 25,
			}
		}

		# important
		super().__init__("readability", config, engine_ext)

	def logic(self, html: str, title: str = "") -> str:
		"""Convert HTML to Markdown using readability
		:param html: original html string
		:param title: page title, defaults to ""
		:return: markdown string
		"""

		# Common configuration parameters by readability:
		config = self.config["engine"]

		doc = Document(
			html,
			min_text_length=config["min_text_length"],
		)
		return f"# {title}\n\n{self.html_to_markdown(doc.summary())}"  # use markdownify
