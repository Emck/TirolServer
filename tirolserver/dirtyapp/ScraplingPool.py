"""Scrapling Pool"""

from __future__ import annotations

import asyncio

from generic_connection_pool.asyncio import BaseConnectionManager
from scrapling.fetchers import AsyncStealthySession

import tirolserver.config as config
from tirolserver.commons import logger
from tirolserver.commons.type import FetchRequest
from tirolserver.core import FetcherSession


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
		"""Fetch web pages
		:param request: request parameters
		:return: response data
		"""
		self.times += 1  # update usage times
		response = await FetcherSession(self.stealthy, request)
		logger.debug(f"[PoolObj] call fetch status={response['status']}")
		return response


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
