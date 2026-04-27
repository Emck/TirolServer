"""Cleaner Content"""

import re

import html2text
import trafilatura
from bs4 import BeautifulSoup

# import pickle


class CleanerContent:
	"""Clean content from HTML based on Trafilatura + BeautifulSoup"""

	REMOVE_TAGS = ["script", "style", "noscript", "iframe", "svg", "form", "button", "input", "select", "textarea", "canvas"]
	"""need to remove tags completely"""

	EXCLUDE_PATTERN = re.compile(r".*?\b(ad|ads|advert|banner|popup|social|share|promo)\b.*", re.I)
	"""need to remove some class/id keywords"""

	WHITELIST_PATTERN = re.compile(r"article|content|post|entry|main", re.I)
	"""define whitelist keywords"""

	def clean(self, url: str, title: str, html: str, include_links: bool = True) -> str:
		"""Clean HTML and return the main content
		:param html: original HTML content
		:param include_links: include links
		:return: cleaned content string
		"""

		if not html:
			return ""

		# Perform core extraction using Trafilatura (Subject positioning, noise removal, code repair)
		content = trafilatura.extract(
			html,
			output_format="markdown",
			include_links=include_links,
			include_tables=True,  # keep table
			include_images=False,  # remove image tags
			include_comments=False,  # exclude comments
			no_fallback=False,  # try more algorithms if extraction fails
		)

		# fails or too short, fallback to BeautifulSoup
		if not content or len(content) < 200:
			content = self._BeautifulSoup(html, include_links)

		return content

	def _BeautifulSoup(self, html: str, preserve_links: bool = True) -> str:
		"""Clean HTML using BeautifulSoup
		:param html: original HTML content
		:param preserve_links: include links
		:return: cleaned content string
		"""

		# pickle.dump(ht)

		if not html:
			return ""

		# 检查  BeautifulSoup 库的使用
		soup = BeautifulSoup(html, "lxml")

		# 1. remove noise tags
		for tag in self.REMOVE_TAGS:
			for element in soup.find_all(tag):
				element.decompose()

		# 2. precise location, if not found, use full body
		main_content = self._find_main_content(soup)
		target_node = main_content if main_content else soup.body
		if not target_node:
			return ""

		# 3. cautious cleaning, remove unsafe tags
		to_decompose = set()
		for element in target_node.find_all(True):
			if not preserve_links and element.name == "a":
				to_decompose.add(element)
				continue

			attrs_dict = getattr(element, "attrs", {})
			cls = attrs_dict.get("class", [])
			cls_str = " ".join(cls) if isinstance(cls, list) else str(cls)
			element_id = str(attrs_dict.get("id", ""))
			combined_attr = f"{cls_str} {element_id}"

			if self.WHITELIST_PATTERN.search(combined_attr):
				continue

			if self.EXCLUDE_PATTERN.match(combined_attr):
				to_decompose.add(element)

		# 4. execute delete
		for node in to_decompose:
			try:
				if node.parent:
					node.decompose()
			except Exception:
				pass

		# 5. get safe title
		title_str = ""
		if soup.title and soup.title.string:
			title_str = f"# {soup.title.string.strip()}\n\n"

		# 6. convert to markdown
		# 检查  HTML2Text 库的使用

		md_converter = html2text.HTML2Text()
		md_converter.body_width = 0  # no line break
		md_converter.unicode_snob = True  # keep unicode characters
		md_converter.ignore_images = True  # remove images
		md_converter.protect_links = True  # protect from line breaks
		md_converter.ignore_emphasis = False  # keep emphasis
		md_converter.ignore_links = not preserve_links  # remove links if not preserved

		try:
			markdown_text = md_converter.handle(str(target_node))
			return title_str + self._cleanline(markdown_text)
		except Exception:
			return title_str + target_node.get_text(separator="\n", strip=True)

	def _find_main_content(self, soup: BeautifulSoup):
		"""Find main content in BeautifulSoup
		:param soup: BeautifulSoup object
		:return: main content node
		"""
		for tag in ["article", "main"]:
			found = soup.find(tag)
			if found:
				return found

		# find common main content
		patterns = [r"article-body", r"post-content", r"entry-content", r"main-content", r"article-content"]
		for p in patterns:
			found = soup.find(class_=re.compile(p, re.I)) or soup.find(id=re.compile(p, re.I))
			if found:
				return found
		return None

	def _cleanline(self, text: str) -> str:
		"""Clean line breaks in markdown text
		:param text: string
		:return: string
		"""

		lines = [line.strip() for line in text.splitlines()]
		cleaned_lines = []
		for i, line in enumerate(lines):
			if line:
				cleaned_lines.append(line)
			else:
				if i > 0 and cleaned_lines and cleaned_lines[-1] != "":
					cleaned_lines.append("")

		cleantext = "\n".join(cleaned_lines)
		cleantext = re.sub(r"\n{3,}", "\n\n", cleantext)

		return cleantext.strip()
