"""Logger module"""

import logging

"""init logger"""

# disabled the logs of third-party libraries
logging.getLogger("gunicorn.access").disabled = True  # disable gunicorn.access log
logging.getLogger("scrapling").disabled = True  # disable scrapling logs
logging.getLogger("unstructured").setLevel(logging.ERROR)  # set unstructured logger level to ERROR

# get logger from gunicorn
gunicorn_logger = logging.getLogger("gunicorn.error")
gunicorn_logger.setLevel(logging.INFO)
