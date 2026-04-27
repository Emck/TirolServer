"""Logger module"""

import logging


def disabled_logger():
	"""disabled the logs of third-party libraries"""
	logging.getLogger("uvicorn.access").disabled = True  # disable uvicorn.access log
	logging.getLogger("scrapling").disabled = True  # Block scrapling logs


"""init logger"""
# get logger from gunicorn
gunicorn_logger = logging.getLogger("gunicorn.error")
gunicorn_logger.setLevel(logging.INFO)


disabled_logger()  # default disabled the logs of third-party libraries


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
