"""Type module"""

from dataclasses import dataclass


@dataclass
class FetchRequest:
	"""request parameters
	:param url: The target URL to retrieve data from.
	:param timeout: The maximum time in seconds to wait for a response.
	"""

	url: str
	timeout: int = 30


@dataclass
class FetchResponse:
	"""response parameters
	:param title: page title
	:param body: page body
	:param error: error message
	"""

	title: str | None = None
	body: str | None = None
	error: str | None = None
