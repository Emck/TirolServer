"""api/v2 routers"""

from fastapi import APIRouter

from ....utils import router_path
from .test import test

#: fastapi routers /api/v2/*
_router_api_v2: APIRouter = APIRouter()

# add test
_router_api_v2.add_api_route(router_path(__file__, test), test, methods=["GET"])

__all__ = [
	"_router_api_v2",
]
