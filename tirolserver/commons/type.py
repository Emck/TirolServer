"""Type module"""

from dataclasses import dataclass


@dataclass
class WebPageResponse:
	"""response web page info
	:param title: page title
	:param content: page content
	"""

	title: str | None = None
	content: str | None = None


@dataclass
class FetchRequest:
	"""fetch request parameters
	:param url: The target URL to retrieve data from.
	:param timeout: The maximum time in seconds to wait for a response.
	"""

	url: str | None = None
	timeout: int = 30
	clean: bool = True


@dataclass
class FetchResponse(WebPageResponse):
	"""fetch response parameters"""

	pass


@dataclass
class CleanHtmlRequest:
	"""request parameters
	:param url: The target URL to retrieve data from.
	:param html: The target URL html content.
	:param title: The target URL html title.
	:param timeout: The maximum time in seconds to wait for cleanHtml request.
	"""

	url: str | None = None
	html: str = ""
	title: str = ""
	timeout: int = 10


@dataclass
class CleanHtmlResponse(WebPageResponse):
	"""cleanhtml response parameters"""

	pass
