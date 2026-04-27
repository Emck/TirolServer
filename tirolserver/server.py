import sys

import gunicorn.app.wsgiapp
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from tirolserver.commons import logger
from tirolserver.routers import router_api

# create app
app: FastAPI = FastAPI(title="Tirol Server")
"""FastAPI instance"""


# include routes
app.include_router(router_api)


@app.exception_handler(404)
@app.exception_handler(HTTPException)
@app.exception_handler(Exception)
async def _exception_handler(request: Request, exc: Exception) -> JSONResponse:
	"""exception handler by fastapi.
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


"""main function"""


def main():
	"""main function"""
	sys.argv = ["gunicorn", "tirolserver.server:app", "-c", "tirolserver/config.py"]
	gunicorn.app.wsgiapp.run()


if __name__ == "__main__":
	main()
