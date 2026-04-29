import asyncio
import hashlib
import os
import secrets

import lmdb
import lmdb.aio


class DataBase:
	"""DataBase class"""

	_instance = None
	_owner_pid = None

	def __new__(cls, *args, **kwargs):
		if cls._instance is None or cls._owner_pid != os.getpid():
			cls._instance = super().__new__(cls)
			cls._instance._env = None
			cls._owner_pid = os.getpid()
			cls._instance._initialized = False
		return cls._instance

	def __init__(self, db_path="tirolserver/database"):
		if getattr(self, "_initialized", False):
			return

		min_size = 16 * 1024**2
		actual_size = min_size
		if os.path.exists(os.path.join(db_path, "data.mdb")):
			temp_env = lmdb.open(db_path, readonly=True, max_dbs=2, lock=True)
			actual_size = temp_env.info()["map_size"]
			temp_env.close()
		final_size = max(min_size, actual_size)
		self._env = lmdb.open(db_path, max_dbs=2, map_size=final_size, writemap=True, map_async=True)
		self.url_db = self._env.open_db(b"clean_url", dupsort=True)
		self.rule_db = self._env.open_db(b"clean_rule")
		self.aenv = lmdb.aio.wrap(self._env)
		self._initialized = True
		print("✅ Database is initialized")

	async def __aenter__(self):
		return self

	async def __aexit__(self, exc_type, exc_val, exc_tb):
		self.close()

	async def put(self, key: str, value: bytes, retry: int = 3):
		data_id = secrets.token_bytes(16)  # generate id
		index_value = data_id + self._get_hash(value)
		try:
			async with self.aenv.begin(write=True) as txn:
				await txn.put(key.encode(), index_value, db=self.url_db, dupdata=True)  # save id to index db
				await txn.put(data_id, value, db=self.rule_db)  # save value to data db
		except lmdb.MapFullError:
			if retry <= 0:
				raise
			curr_size = self._env.info()["map_size"]
			self._env.set_mapsize(curr_size * 1.5)
			await self.put(key, value, retry - 1)

	async def get(self, key: str) -> list[bytes]:
		async with self.aenv.begin(write=False) as txn:
			async with txn.cursor(db=self.url_db) as cursor:
				if not await cursor.set_key(key.encode()):
					return []
				index_values = await cursor.iternext_dup()  # get all index values
				tasks = [txn.get(iv[:16], db=self.rule_db) for iv in index_values]
				results = await asyncio.gather(*tasks)
				return [r for r in results if r is not None]

	async def remove(self, key: str, value: bytes = None) -> bool:
		async with self.aenv.begin(write=True) as txn:
			async with txn.cursor(db=self.url_db) as cursor:
				if not await cursor.set_key(key.encode()):
					return False
				index_values = await cursor.iternext_dup()
				if value is None:  # del all values
					for iv in index_values:
						await txn.delete(iv[:16], db=self.rule_db)
					await txn.delete(key.encode(), db=self.url_db)
					return True
				else:  # del specific value
					target_hash = self._get_hash(value)
					for iv in index_values:
						if iv[16:] == target_hash:
							data_id = iv[:16]
							actual_val = await txn.get(data_id, db=self.rule_db)
							if actual_val == value:
								await txn.delete(data_id, db=self.rule_db)
								await txn.delete(key.encode(), iv, db=self.url_db)
								return True
		return False

	def close(self):
		"""close database"""
		if self._env:
			self._env.close()
			self._env = None
			self._initialized = False
			DataBase._instance = None
			print("✅ Database is closed")
		else:
			print("❌ Database not initialized")

	def _get_hash(self, data: bytes) -> bytes:
		return hashlib.blake2b(data, digest_size=8).digest()  # 8 byte hash
