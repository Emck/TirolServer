# https://crawl4ai.com
# https://github.com/unclecode/crawl4ai

from .base import CleanBase


# deprecated
class Crawl4aiCleaner(CleanBase):
	"""Crawl4ai Cleaner"""

	def __init__(self, config: dict = {}, engine_ext: dict = {}):
		# default engine config
		config = {
			"engine": {},
		}

		# important
		super().__init__("crawl4ai", config, engine_ext)

	def logic(self, html: str, title: str = "") -> str:
		"""Convert HTML to Markdown using Crawl4ai
		:param html: original html string
		:param title: page title, defaults to ""
		:return: markdown string
		"""

		return "can not run crawl4ai cleaner"
