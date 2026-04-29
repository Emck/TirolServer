"""api routers"""

from fastapi import APIRouter

from ...utils import router_path
from .cleanhtml import CleanHtmlResponse, cleanhtml
from .web_fetch import WebFetchResponse, web_fetch

#: fastapi routers /api/*
_router_api: APIRouter = APIRouter()

# add web_fetch
_router_api.add_api_route(router_path(__file__, web_fetch), web_fetch, methods=["POST"], response_model=WebFetchResponse, response_model_exclude_none=True)
# add cleanhtml
_router_api.add_api_route(router_path(__file__, cleanhtml), cleanhtml, methods=["POST"], response_model=CleanHtmlResponse, response_model_exclude_none=True)


__all__ = [
	"_router_api",
]
