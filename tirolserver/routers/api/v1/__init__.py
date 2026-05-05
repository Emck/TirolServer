"""api/v1 routers"""

from fastapi import APIRouter

from ....utils import router_path
from .cleanhtml import CleanHtmlResponse, cleanhtml
from .web_fetch import WebFetchResponse, web_fetch
from .web_search import WebSearchResponse, web_search

#: fastapi routers /api/v1/*
_router_api_v1: APIRouter = APIRouter()


# add web_fetch
_router_api_v1.add_api_route(router_path(__file__, web_fetch), web_fetch, methods=["POST"], response_model=WebFetchResponse, response_model_exclude_none=True)
# add web_search
_router_api_v1.add_api_route(router_path(__file__, web_search), web_search, methods=["POST"], response_model=WebSearchResponse, response_model_exclude_none=True)
# add cleanhtml
_router_api_v1.add_api_route(router_path(__file__, cleanhtml), cleanhtml, methods=["POST"], response_model=CleanHtmlResponse, response_model_exclude_none=True)


__all__ = [
	"_router_api_v1",
]
