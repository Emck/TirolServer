from selectolax.parser import HTMLParser

from .base import CleanBase


class SimpleRemoveCleaner(CleanBase):
	"""SimpleRemove Cleaner (Fallback)
	only remove navigation, footer, header, ads from HTML before converting to Markdown
	"""

	def __init__(self, config: dict = {}, engine_ext: dict = {}):
		# default engine config
		config = {
			"engine": {
				"tags": ["script", "noscript", "header", "footer", "nav", "ads", "style", "iframe", "svg"],
			}
		}
		# remove tags from deltags
		if engine_ext.get("deltags"):
			for tag in engine_ext.get("deltags"):
				config["engine"]["tags"].remove(tag)
			engine_ext.pop("deltags")

		# important
		super().__init__("simple_remove", config, engine_ext)

	def logic(self, html: str, title: str = "") -> str:
		"""Convert HTML to Markdown (Fallback)
		:param html: original html string
		:param title: page title, defaults to ""
		:return: markdown string
		"""

		# Common configuration parameters by HTMLParser:
		config = self.config["engine"]

		body = HTMLParser(html).css_first("body")
		body_tree = HTMLParser(body.html if body else "")
		tags = ", ".join(config["tags"])  # splicing css selector parameters
		for tag in body_tree.css(tags):
			tag.decompose()  # remove tags

		return f"# {title}\n\n{self.html_to_markdown(body_tree.html)}"  # use markdownify
