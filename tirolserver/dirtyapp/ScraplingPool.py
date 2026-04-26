"""Scrapling Pool"""

from __future__ import annotations

import asyncio

from generic_connection_pool.asyncio import BaseConnectionManager
from scrapling.fetchers import AsyncStealthySession

import tirolserver.config as config
from tirolserver.commons import FetchRequest, logger


class PoolObject:
	"""Pool Object Class"""

	def __init__(self):
		self.times: int = 0
		"""save the usage times of internal objects"""
		self.stealthy: AsyncStealthySession = None
		"""internal object instance"""

	async def init(self) -> PoolObject:
		"""Init internal object
		:return: myself instance
		"""
		try:
			async with asyncio.timeout(config.Pool_Object_create_timeout):
				self.stealthy = AsyncStealthySession(
					headless=config.Pool_Object_stealthy_headless,
					network_idle=config.Pool_Object_stealthy_network_idle,
				)
				await self.stealthy.start()  # very important

			logger.debug(f"[PoolObj] created {hex(id(self))}")
		except asyncio.TimeoutError:
			logger.debug("[PoolObj] create timeout exception")
			await self.close()
		finally:
			return self

	async def check(self) -> bool:
		"""Checks internal object is alive
		:return: ``True`` if internal object is alive otherwise ``False``
		"""
		logger.debug("[PoolObj] checking...")

		# check as failed after using the maximum number of times
		if config.Pool_max_usage_times and self.times >= config.Pool_max_usage_times:
			return False

		return True

	async def close(self):
		"""Close internal object"""
		try:
			await self.stealthy.close()  # very important
			logger.debug(f"[PoolObj] closed {hex(id(self))}")
		except Exception:
			logger.debug(f"[PoolObj] closed {hex(id(self))} exception")

	"""
	Pool Object Function
	"""

	async def fetch(self, request: FetchRequest) -> dict:
		"""Use AsyncStealthySession to fetch web pages
		:param request: request parameters
		:return: response data
		"""
		if request.url is None or not request.url.startswith(("http://", "https://")):
			return {"status": 500, "error": "url is invalid"}
		if self.stealthy is None:
			return {"status": 500, "error": "pool object is none"}

		try:
			self.times += 1  # update usage times
			response = await self.stealthy.fetch(url=request.url, timeout=request.timeout * 1000)
			if response.status != 200:
				logger.debug(f"[PoolObj] call fetch error status={response.status}")
				return {"status": response.status, "error": response.reason}

			logger.debug(f"[PoolObj] call fetch status={response.status}")
			return {
				"status": response.status,
				"title": response.css("title::text").get(),
				"body": response.body.decode("utf-8", errors="ignore"),
			}
		except RuntimeError as e:  # catch scrapling fetch RuntimeError
			return {"status": 500, "error": "fetch runtime error: " + str(e)}
		except Exception as e:
			if "TimeoutError" in str(type(e)):
				return {"status": 500, "error": "fetch timeout: " + str(e)}
			elif "net::ERR_NAME_NOT_RESOLVED" in str(e):
				return {"status": 500, "error": "fetch error: target host name not resolved"}
			elif "net::ERR_CONNECTION_REFUSED" in str(e):
				return {"status": 500, "error": "fetch error: target server refused connection"}
			return {"status": 500, "error": "fetch exception: " + str(type(e)) + " " + str(e)}


class PoolObjectManager(BaseConnectionManager[str, PoolObject]):
	"""Pool Object Manager Class
	This class inherits from BaseConnectionManager, Define the objects for pool management
	"""

	async def create(self, endpoint: str) -> PoolObject:
		"""Create a new object instance.
		:param endpoint: endpoint to object to
		:return: new object instance
		"""
		return await PoolObject().init()  # must call init()

	async def dispose(self, endpoint: str, object: PoolObject):
		"""Disposes the object.
		:param endpoint: endpoint to object to
		:param object: object to be closed
		"""
		await object.close()

	async def check_aliveness(self, endpoint: str, object: PoolObject) -> bool:
		"""Checks that the object is alive.
		:param endpoint: endpoint to object to
		:param object: object to be checked
		:return: ``True`` if object is alive otherwise ``False``
		"""
		return await object.check()

	async def on_connection_dead(self, endpoint: str, object: PoolObject):
		"""On object is dead, triggered when the object checked is inactive.
		:param endpoint: endpoint to object to
		:param object: object to be dead
		"""
		logger.debug(f"[PoolManager] on_connection_dead {hex(id(object))}")
		await self.dispose(endpoint, object)  # need dispose object

	# async def on_acquire(self, endpoint: str, object: PoolObject) -> None:
	# 	pass

	# async def on_release(self, endpoint: str, object: PoolObject) -> None:
	# 	pass
