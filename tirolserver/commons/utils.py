"""Utils module"""

import argparse
import sys

import html2text
from fastapi import HTTPException, Request

from tirolserver.commons import MakeLogText, logger


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


async def makeHTTPException(raw: Request, status: int, error: str) -> HTTPException:
	"""make HTTPException class based on the parameters.
	:param raw: original request
	:param status: http status
	:param error: exception message string
	:return: HTTPException
	"""
	logger.info(await MakeLogText(raw=raw, status=status, error=error))
	return HTTPException(status_code=status, detail=error)


async def CleanHtmlData(data: str) -> str:
	"""Clean the html page content
	:param data: page content
	:return: cleaned page content
	"""
	return await Body2Text(data)


async def Body2Text(data: str) -> str:
	"""Convert HTTP responses to plain text (Markdown style)
	:param data: _description_
	:raises ValueError: _description_
	:return: _description_
	"""
	if data is None:
		raise ValueError("data is None")

	h = html2text.HTML2Text()
	h.ignore_links = False  # keep links
	h.ignore_images = True  # block images (models usually do not require image links)
	h.ignore_emphasis = False  # keep bold/italic
	h.body_width = 0  # o = no line breaks
	return h.handle(data)
