"""Fetcher Url"""

from scrapling.fetchers import AsyncStealthySession

from tirolserver.commons.type import FetchRequest


async def FetcherSession(stealthy: AsyncStealthySession, request: FetchRequest) -> dict:
	"""Use AsyncStealthySession to fetch web pages
	:param request: request parameters
	:return: response data, {"status": int, "title": str=None, "body": str=None, "detail": str=None}
	"""
	if request.url is None or not request.url.startswith(("http://", "https://")):
		return {"status": 500, "detail": "url is invalid"}
	if stealthy is None:
		return {"status": 500, "detail": "pool object is none"}

	try:
		response = await stealthy.fetch(url=request.url, timeout=request.timeout * 1000)
		if response.status != 200:
			return {"status": response.status, "detail": response.reason}

		return {
			"status": response.status,
			"title": response.css("title::text").get(),
			"body": response.body.decode("utf-8", errors="ignore"),
		}
	except RuntimeError as e:  # catch scrapling fetch RuntimeError
		return {"status": 500, "detail": f"runtime error: {str(e)}"}
	except Exception as e:
		if "TimeoutError" in str(type(e)):
			return {"status": 500, "detail": f"timeout {str(type(e))}"}
		elif "net::ERR_NAME_NOT_RESOLVED" in str(e):
			return {"status": 500, "detail": "target host name not resolved"}
		elif "net::ERR_CONNECTION_REFUSED" in str(e):
			return {"status": 500, "detail": "target server refused connection"}
		return {"status": 500, "detail": f"exception: {str(type(e))} {str(e)}"}
