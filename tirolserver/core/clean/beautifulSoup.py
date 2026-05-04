from bs4 import BeautifulSoup
from selectolax.parser import HTMLParser

from .base import CleanBase


# deprecated
class BeautifulSoupCleaner(CleanBase):
	"""BeautifulSoup Cleaner"""

	def __init__(self, config: dict = {}, engine_ext: dict = {}):
		# default engine config
		config = {
			"engine": {
				"features": "lxml",
			}
		}

		# important
		super().__init__("beautifulsoup", config, engine_ext)

	def logic(self, html: str, title: str = "") -> str:
		"""Convert HTML to Markdown using BeautifulSoup
		:param html: original html string
		:param title: page title, defaults to ""
		:return: markdown string
		"""

		# Common configuration parameters by BeautifulSoup:
		config = self.config["engine"]

		body = HTMLParser(html).css_first("body")  # get body element
		soup = BeautifulSoup(
			body.html if body else html,
			features=config["features"],
		)
		return f"# {title}\n\n{self.html_to_markdown(str(soup))}"  # use markdownify
