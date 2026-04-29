"""utils on router"""

import argparse
import logging
import sys
from pathlib import Path

from fastapi import Request

_routerPath: Path = Path(__file__).parent.joinpath("../routers").resolve()


def router_path(file: str, obj: classmethod) -> str:
	try:
		return (str(Path(file).parent) + "/").replace(str(_routerPath), "") + obj.__name__
	except Exception:
		return obj.__name__


def get_clean_db(request: Request):
	return request.app.state.cleandb


async def argsparse(Host: str, Port: int):
	"""sys args parse.
	:param Host: Listen Host
	:param Port: Listen Port
	:return: Namespace: host, port, run
	"""
	args = argparse.Namespace(host=Host, port=Port)
	if sys.argv[0].endswith(".py"):  # python mode
		parser = argparse.ArgumentParser(add_help=False)
		parser.add_argument("--host", type=str, default=args.host)
		parser.add_argument("--port", type=int, default=args.port)
		args, _ = parser.parse_known_args()
		args.run = "python"
	elif sys.argv[0].endswith("uvicorn"):  # uvicorn mode
		parser = argparse.ArgumentParser(add_help=False)
		parser.add_argument("--host", type=str, default=args.host)
		parser.add_argument("--port", type=int, default=args.port)
		args, _ = parser.parse_known_args()
		args.run = "uvicorn"
	elif sys.argv[0].endswith("gunicorn"):  # gunicorn mode
		parser = argparse.ArgumentParser(add_help=False)
		parser.add_argument("--bind", type=str, default=f"{args.host}:{args.port}")
		args, _ = parser.parse_known_args()
		host, port = args.bind.rsplit(":", 1)
		args = argparse.Namespace(host=host, port=int(port), run="gunicorn")
	return args


def enable_pool_logger(level=logging.info) -> logging.Logger:
	"""enable pool logger
	:param level: logging level, defaults to logging.info
	:return: logger
	"""
	pool_logger = logging.getLogger("generic_connection_pool")
	pool_logger.setLevel(logging.DEBUG)
	if not pool_logger.handlers:
		handler = logging.StreamHandler()
		handler.setFormatter(logging.Formatter("[%(asctime)s] [%(process)d] [%(levelname)s] 🌹 %(message)s", datefmt="%Y-%m-%d %H:%M:%S %z"))
		pool_logger.addHandler(handler)
