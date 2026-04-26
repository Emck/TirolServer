"""api router"""

from dataclasses import asdict

from fastapi import APIRouter, HTTPException, Request
from gunicorn.dirty import get_dirty_client_async

import tirolserver.config as config
from tirolserver.commons import CleanHtmlData, FetchRequest, FetchResponse, MakeLogText, logger, makeHTTPException

router_api: APIRouter = APIRouter()
"""fastapi router /api/*"""


@router_api.post("/api/web_fetch", response_model=FetchResponse, response_model_exclude_none=True)
async def web_fetch(request: FetchRequest, raw: Request) -> FetchResponse:
	"""web page fetch interface, return to the cleaned web page content.
	:param request: request parameters (include url, timeout, ...)
	:param raw: original request
	:return: response data
	"""
	try:
		# verify parameter
		if request.url is None:
			raise await makeHTTPException(raw, 500, "url is none")
		elif request.timeout > config.Pool_acquire_timeout:
			raise await makeHTTPException(raw, 500, f"timeout set is too large (system max={config.Pool_acquire_timeout})")

		# run dirty func
		client = await get_dirty_client_async()
		result = await client.execute_async(config.dirty_apps[0], "fetch", asdict(request))
		if result["status"] == 200:
			logger.info(await MakeLogText(raw, 200))
			body = await CleanHtmlData(result["body"])  # clean data
			return FetchResponse(title=result["title"], body=body)
		else:
			raise await makeHTTPException(raw, result["status"], result["error"])

	except HTTPException as e:
		raise e
	except Exception as e:
		raise await makeHTTPException(raw, 502, "unknow exception " + str(type(e)) + " " + str(e))
