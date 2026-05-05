from .api.testdb import _router_api_testdb as router_api_testdb
from .api.v1 import _router_api_v1 as router_api_v1
from .api.v2 import _router_api_v2 as router_api_v2

__all__ = [
	"router_api_testdb",
	"router_api_v1",
	"router_api_v2",
]
