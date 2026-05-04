"""Scrapling App"""

import asyncio
import os
import threading

from generic_connection_pool.asyncio import ConnectionPool
from gunicorn.dirty import DirtyApp, DirtyTimeoutError

import tirolserver.config as config
from tirolserver.dirtyapp.ScraplingPool import PoolObject, PoolObjectManager
from tirolserver.utils import logger


class App(DirtyApp):
	"""Scrapling App Class (DirtyApp)"""

	def __init__(self):
		super().__init__()

		self.pool: ConnectionPool[str, PoolObject] = None
		"""manager object pool"""
		self.loop: asyncio.AbstractEventLoop = None
		"""event loop"""

	def _run_event_loop(self):
		"""The background thread is responsible for running all asynchronous tasks."""
		asyncio.set_event_loop(self.loop)
		self.loop.run_forever()

	def init(self):
		"""Init async event Loop and init pool."""
		# enable_pool_logger()  # debug generic_connection_pool

		# create event loop
		self.loop = asyncio.new_event_loop()

		# start the loop in an independent thread
		self.thread = threading.Thread(target=self._run_event_loop, daemon=True)
		self.thread.start()

		# run self._initPool() in thread
		asyncio.run_coroutine_threadsafe(self._initPool(), self.loop).result()

	async def _initPool(self):
		"""Init pool and activate one instance."""
		self.pool = ConnectionPool[str, PoolObject](
			connection_manager=PoolObjectManager(),
			max_size=config.Pool_max_size,
			total_max_size=config.Pool_total_max_size,
			min_idle=config.Pool_min_idle,
			idle_timeout=config.Pool_idle_timeout,
			max_lifetime=config.Pool_max_lifetime,
			acquire_timeout=config.Pool_acquire_timeout,
			dispose_timeout=config.Pool_dispose_timeout,
			background_collector=config.Pool_background_collector,
		)
		# activate one instance (hot loading logic)
		try:
			async with self.pool.connection(endpoint="dirty", timeout=config.Pool_acquire_timeout) as _instance:
				logger.info(f"[Dirty-{os.getpid()}] Initializing pool siez={self.pool.get_size()})")
				logger.debug(f"[Dirty-{os.getpid()}] Hot loading instance {hex(id(_instance))}")
				pass
		except TimeoutError:
			logger.debug(f"[Dirty-{os.getpid()}] Initializing complete, Hot loading failure❌ pool siez={self.pool.get_size()}")

	def close(self):
		"""Close pool, stop self.loop, stop thread."""
		# run await self.pool.close() in thread
		if self.pool:
			try:
				asyncio.run_coroutine_threadsafe(self.pool.close(), self.loop).result(timeout=config.Pool_acquire_timeout)
			except Exception as e:
				logger.info(f"[Dirty-{os.getpid()}] Pool colsed exception❌ " + str(e))

		# run self.loop.stop() in self.loop
		if self.loop.is_running():
			self.loop.call_soon_threadsafe(self.loop.stop)

		# stop thread
		if self.thread.is_alive():
			self.thread.join(timeout=20)
			if self.thread.is_alive():
				logger.info(f"[Dirty-{os.getpid()}] Stop event loop thread failure❌ ")
				return

		logger.info(f"[Dirty-{os.getpid()}] resources cleaned up safely")

	"""
	Dirty Function
	"""

	def fetch(self, req: dict) -> dict:
		"""web fetch
		:param request: request parameters
		:return: response data
		"""
		return asyncio.run_coroutine_threadsafe(self._fetch_async(req), self.loop).result()  # run self._fetch_async() in thread

	async def _fetch_async(self, req: dict) -> dict:
		try:
			logger.debug(f"[Dirty-{os.getpid()}] current pool size={self.pool.get_size()}")
			async with asyncio.timeout(config.dirty_timeout - 5):  # timeout by dirty_timeout -5
				async with self.pool.connection(endpoint="dirty", timeout=config.Pool_acquire_timeout) as pool_obj:
					logger.debug(f"[Dirty-{os.getpid()}] current instance {hex(id(pool_obj))}")
					return await pool_obj.fetch(req)  # call pool object function

		except TimeoutError:
			return {"status": 500, "detail": "dirty operation times out"}
		except AttributeError:
			return {"status": 500, "detail": "dirty operation exception object has no attribute"}
		except DirtyTimeoutError:
			return {"status": 500, "detail": "dirty operation DirtyTimeoutError"}
		except Exception as e:
			return {"status": 500, "detail": "dirty operation exception " + str(type(e)) + " " + str(e)}
