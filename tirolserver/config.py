"""Tirol Server"""

#: server bind
bind: str = "127.0.0.1:38080"

#: set proc name, need install setproctitle package
proc_name: str = "TirolWebServer"

#: number of worker processes
workers: int = 2

#: woker class
worker_class: str = "asgi"  # or "uvicorn.workers.UvicornWorker"

#: number of threads by worker processes, need add set worker_class = 'gthread'
# threads: int = 4

#: The maximum number of seconds a Worker can process a request
# timeout: int = 30

#: The time to wait for the Worker to exit gracefully after receiving the close signal
graceful_timeout: int = 10

# : It will automatically restart after processing the specified number of times to prevent memory leaks
# max_requests = 1000

# : Add a random offset to max_requests to prevent all workers from restarting simultaneously
# max_requests_jitter: int = 50

# Dirty worker config

#: enable dirty
dirty: bool = True

#: define dirty_apps (list)
dirty_apps: list[str] = ["tirolserver.dirtyapp.ScraplingApp:App"]

#: dirty workers
dirty_workers: int = 1

#: dirty timeout, the minimum setting is 10 seconds
dirty_timeout: int = 20

#: The time to wait for the dirty to exit gracefully after receiving the close signal
dirty_graceful_timeout: int = 10


#: set logger
#: - info
#: - [info,debug,error]
loglevel: str = "info"  # set level

#: access the log file path.
#: - '-' output to standard output
#: - Example: './logs/access.log'
accesslog: str = "-"

#: error the log file path
#: - '-' output to standard error
#: - Example: './logs/error.log'
errorlo: str = "-"


# config pool
#: maximum number of endpoint connections
Pool_max_size = 10
#: maximum number of pool
Pool_total_max_size = 20
#: minimum number of connections in each endpoint the pool tries to hold
Pool_min_idle = 1
#: pool object idle recycling time
Pool_idle_timeout = 20
#: maximum survival time of the pool object, (3600 = one hour)
Pool_max_lifetime = 40
#: connection acquiring default timeout
Pool_acquire_timeout = dirty_timeout - 5
#: pool object disposal timeout
Pool_dispose_timeout = 10
#: is True starts a background worker that disposes expired and idle connections maintaining requested pool state
Pool_background_collector: bool = True
#: greater than max usage times, will be set inactive
Pool_max_usage_times: int = 3


Pool_Object_create_timeout = Pool_acquire_timeout
Pool_Object_stealthy_headless: bool = True
Pool_Object_stealthy_network_idle: bool = True

if dirty_timeout < 10:
	print("⚠️  You need set config.py dirty_timeout, and > 10")
	raise SystemExit()

# Hooks for demonstration
# def on_starting(server):
# 	pass  # Gunicorn server starting


# def post_fork(server, worker):
# 	pass  # Worker fork finished {worker.pid}


# def when_ready(server):
# 	pass  # Gunicorn server ready
# 	# print(f'HTTP workers: {server.num_workers}')
# 	# print(f'Dirty workers: {server.cfg.dirty_workers}')
# 	# print(f'Dirty apps: {server.cfg.dirty_apps}')


# def post_worker_init(worker):
# 	worker.log.info(f"🔔 Worker {worker.pid} initialized")


# def worker_exit(server, worker):
# 	worker.log.info(f"🔔 Worker {worker.pid} exiting")


# def on_exit(server):
# 	pass  # Gunicorn server exiting


# """About Dirty"""


# def on_dirty_starting(arbiter):
# 	pass  # Dirty arbiter starting


# def dirty_post_fork(arbiter, worker):
# 	pass  # Dirty worker {worker.pid} forked


# def dirty_worker_init(worker):
# 	pass  # Dirty worker {worker.pid} initialized apps


# def dirty_worker_exit(arbiter, worker):
# 	pass  # Dirty worker {worker.pid} exiting
