# https://www.unstructured.io
# https://github.com/Unstructured-IO/unstructured


from unstructured.cleaners.core import clean, clean_extra_whitespace, clean_non_ascii_chars
from unstructured.documents.elements import Element
from unstructured.partition.html import partition_html
from unstructured.staging.base import elements_to_md

from .base import CleanBase


class UnstructuredCleaner(CleanBase):
	"""Unstructured Cleaner"""

	def __init__(self, config: dict = {}, engine_ext: dict = {}):
		# default engine config
		config = {
			"engine": {
				"skip_headers_and_footers": True,  # auto analysis and ignore headers and footers
				"combine_under_n_chars": 100,  # combine under chars to reduce fragmentation, for LLM friendliness
				"post_processors": [  # post processors list
					clean_extra_whitespace,  # remove extra whitespace and newline
					clean_non_ascii_chars,  # remove non-ASCII characters
				],
			}
		}

		# important
		super().__init__("unstructured", config, engine_ext)

	def logic(self, html: str, title: str = "") -> str:
		"""Convert HTML to Markdown using unstructured
		:param html: original html string
		:param title: page title, defaults to ""
		:return: markdown string
		"""

		# Common configuration parameters by unstructured:
		config = self.config["engine"]

		elements: list[Element] = partition_html(
			text=html,
			skip_headers_and_footers=config["skip_headers_and_footers"],
			combine_under_n_chars=config["combine_under_n_chars"],
			post_processors=config["post_processors"],
		)
		for element in elements:
			element.apply(lambda text: clean(text, extra_whitespace=True, bullets=True))  # clean whitespace and bullets

		return f"# {title}\n\n{elements_to_md(elements)}"  # use markdownify
