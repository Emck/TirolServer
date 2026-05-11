"""web_fetch router"""

from dataclasses import asdict, dataclass, field
from typing import Optional

from fastapi import Request
from gunicorn.dirty import get_dirty_client_async

import tirolserver.config as config
from tirolserver.core.markdown import HtmlToMarkdown
from tirolserver.utils import logger


@dataclass
class WebFetchRequest:
	"""web fetch request parameters
	# :param url: target URL.
	# :param formats: fetch formats to return.
	# :param onlyMainContent: Whether to extract only the main content or not.
	# :param timeout: maximum time in seconds to wait for a response.
	# :param proxy: proxy to use for the request. "auto" to use the default proxy.
	"""

	url: str
	formats: list[str] = field(default_factory=lambda: ["markdown"])
	onlyMainContent: bool = True
	timeout: int = 60  # default 60 seconds
	proxy: str = "auto"


@dataclass
class WebFetchMetadata:
	"""web fetch metadata parameters
	# :param title: page title.
	# :param description: page description.
	# :param language: page language.
	# :param sourceURL: page source URL.
	# :param statusCode: fetch status code.
	"""

	title: Optional[str] = None
	description: Optional[str] = None
	language: Optional[str] = None
	sourceURL: Optional[str] = None
	statusCode: int = 200


@dataclass
class WebFetchData:
	"""web fetch data parameters
	# :param content: page content.
	# :param markdown: page markdown content.
	# :param metadata: page metadata.
	"""

	content: Optional[str] = None
	markdown: Optional[str] = None
	metadata: WebFetchMetadata = field(default_factory=WebFetchMetadata)


@dataclass
class WebFetchResponse:
	"""web fetch response parameters

	# :param success: fetch operation successful or not.
	# :param data: fetch data info.
	# :param error: error message.
	"""

	success: bool = False
	data: WebFetchData = field(default_factory=WebFetchData)
	error: Optional[str] = None


def _errorResponse(statusCode: int, message: str) -> WebFetchResponse:
	return WebFetchResponse(data=WebFetchData(metadata=WebFetchMetadata(statusCode=statusCode)), error=message)


async def web_fetch(request: WebFetchRequest, raw: Request) -> WebFetchResponse:
	"""web page fetch interface, return to the cleaned web page content.
	:param request: request parameters (include success, data, error)
	:param raw: original request
	:return: response data
	"""
	try:
		# verify parameter
		if request.url is None:
			logger.info(f'[Main] "{raw.method} {raw.url.path}" - fetch[500] "url is none"')
			return _errorResponse(500, "url is none")
		elif request.timeout > config.Pool_acquire_timeout:
			logger.info(f'[Main] "{raw.method} {raw.url.path}" - fetch[500] "timeout set is too large"')
			return _errorResponse(500, f"timeout set is too large (system max={config.Pool_acquire_timeout})")

		# run dirty func
		client = await get_dirty_client_async()
		result = await client.execute_async(config.dirty_apps[0], "fetch", asdict(request))
		if result["status"] == 200:
			response = WebFetchResponse(success=True, data=WebFetchData(metadata=WebFetchMetadata(title=result["title"], sourceURL=result["url"])))
			if "text" in request.formats:
				response.data.content = result["body"]
			if "markdown" in request.formats:
				markdown = HtmlToMarkdown()
				response.data.markdown, info = markdown.toMarkdown(html=result["body"], title=result["title"], url=request.url)  # transform to markdown
				# markdown.printresult(info) # print info
			logger.info(f'[Main] "{raw.method} {raw.url.path}" - 200 length="original: {len(result["body"])} -> cleaned: {len(response.data.markdown) if response.data.markdown else -1}"')

			# import aiofiles
			# async with aiofiles.open("output.html", "w", encoding="utf-8") as f:
			# 	logger.debug(f"write {len(result['body'])} characters to output.html")
			# 	await f.write(result["body"])
			return response
		else:
			logger.info(f'[Main] "{raw.method} {raw.url.path}" - fetch[{result["status"]}]')
			return _errorResponse(result["status"], result["detail"])

	except Exception as e:
		logger.info(f'[Main] "{raw.method} {raw.url.path}" - fetch[500] "unknow exception"')
		return _errorResponse(500, f"unknow exception {str(type(e))} {str(e)}")
