"""utils on router"""

from pathlib import Path


def _routerPath(file: str, obj: classmethod) -> str:
	try:
		path = str(Path(file).parent) + "/"
		path = path.replace(str(Path(__file__).parent), "")
		return path + obj.__name__
	except Exception:
		return ""
