"""api routers"""

from fastapi import APIRouter

from tirolserver.commons.type import CleanHtmlResponse, FetchResponse

from ..utils import _routerPath
from .cleanhtml import cleanhtml
from .web_fetch import web_fetch

_router_api: APIRouter = APIRouter()
"""fastapi routers /api/*"""

# add web_fetch
_router_api.add_api_route(_routerPath(__file__, web_fetch), web_fetch, methods=["POST"], response_model=FetchResponse, response_model_exclude_none=True)
# add cleanhtml
_router_api.add_api_route(_routerPath(__file__, cleanhtml), cleanhtml, methods=["POST"], response_model=CleanHtmlResponse, response_model_exclude_none=True)


__all__ = [
	"_router_api",
]
