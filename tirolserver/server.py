import os
import sys
from contextlib import asynccontextmanager

import gunicorn.app.wsgiapp
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

import tirolserver.config as config
import tirolserver.routers as routers
from tirolserver.core import DataBase
from tirolserver.utils import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
	"""lifespan of fastapi.
	:param app: fastapi instance
	"""

	logger.info(f"🔔 Worker {os.getpid()} lifespan Startup")
	app.state.cleandb = DataBase()

	yield
	logger.info(f"🔔 Worker {os.getpid()} lifespan Shutdown")
	app.state.cleandb.close()


#: fastapi instance
app: FastAPI = FastAPI(title="Tirol Server", lifespan=lifespan)

# auto include routes
for router in routers.__all__:
	app.include_router(getattr(routers, router))


@app.exception_handler(404)
@app.exception_handler(HTTPException)
@app.exception_handler(Exception)
async def _exception_handler(request: Request, exc: Exception) -> JSONResponse:
	"""exception handler of fastapi.
	:param request: original request
	:param exc: Exception instance
	:return: json format response
	"""

	info = f'[Main] "{request.method} {request.url.path}" -'
	if "HTTPException" in str(type(exc)):
		logger.info(f"{info} {exc.status_code} {exc.detail}")
		return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

	errstr = f"unknow exception {str(type(exc))} {str(exc)}"
	logger.info(f"{info} 500 {errstr}")
	return JSONResponse(status_code=500, content={"detail": errstr})


@app.middleware("http")
async def custom_http_header(request: Request, call_next):
	if request.method in ("POST"):
		content_length = request.headers.get("Content-Length")
		if content_length and int(content_length) > config.content_max_size:
			return JSONResponse(status_code=413, content={"detail": f"content length too large. Limit is {config.content_max_size} bytes."})

	response = await call_next(request)
	response.headers["Server"] = config.headerServer  # change server header
	return response


def main():
	"""main function"""
	sys.argv = ["gunicorn", "tirolserver.server:app", "-c", "tirolserver/config.py"]
	gunicorn.app.wsgiapp.run()


if __name__ == "__main__":
	main()
