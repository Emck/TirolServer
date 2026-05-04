import asyncio
import copy
import hashlib
import os
import secrets

import lmdb
import msgpack

from tirolserver.utils import merge_dict_deep


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
		self._initialized = True
		print("✅ Database is initialized")

	def put(self, key: str, value: bytes, retry: int = 3):
		data_id = secrets.token_bytes(16)  # generate id
		index_value = data_id + self._make_hash(value)
		try:
			with self._env.begin(write=True) as txn:
				txn.put(key.encode(), index_value, db=self.url_db, dupdata=True)  # save id to index db
				txn.put(data_id, value, db=self.rule_db)  # save value to data db
		except lmdb.MapFullError:
			if retry <= 0:
				raise
			curr_size = self._env.info()["map_size"]
			self._env.set_mapsize(curr_size * 1.5)
			self.put(key, value, retry - 1)

	def get(self, key: str) -> list[bytes]:
		result = []
		with self._env.begin(write=False) as txn:
			with txn.cursor(db=self.url_db) as cursor:
				if not cursor.set_key(key.encode()):
					return result
				for iv in cursor.iternext_dup():  # get all index values
					value = txn.get(iv[:16], db=self.rule_db)
					if value is not None:
						result.append(value)
		return result

	def remove(self, key: str, value: bytes = None) -> bool:
		with self._env.begin(write=True) as txn:
			with txn.cursor(db=self.url_db) as cursor:
				if not cursor.set_key(key.encode()):
					return False
				index_values = cursor.iternext_dup()
				if value is None:  # del all values
					for iv in index_values:
						txn.delete(iv[:16], db=self.rule_db)
					txn.delete(key.encode(), db=self.url_db)
					return True
				else:  # del specific value
					target_hash = self._get_hash(value)
					for iv in index_values:
						if iv[16:] == target_hash:
							data_id = iv[:16]
							actual_val = txn.get(data_id, db=self.rule_db)
							if actual_val == value:
								txn.delete(data_id, db=self.rule_db)
								txn.delete(key.encode(), iv, db=self.url_db)
								return True
		return False

	def find(self, url: str) -> list[bytes]:
		if not url:
			return []
		search_key = url.encode()
		result = []

		with self._env.begin(write=False) as txn:
			with txn.cursor(db=self.url_db) as cursor:
				found = cursor.set_range(search_key)  # find first >= search_key
				if not found:  # if not found, go back to last key
					if not cursor.last():
						return []
				else:  # if found but not exact match, go back one step
					if cursor.key() != search_key:
						if not cursor.prev():  # only one data and it's greater than search_key
							curr_k = cursor.key()
							if curr_k and search_key.startswith(curr_k):
								self._get_all_dups(cursor, txn, result)
							return result

				# traverse backward to find all rules with same prefix
				first_int = search_key[0]  # extract first byte for quick break
				while True:
					if not (current_key := cursor.key()):
						break
					if search_key.startswith(current_key):  # core: url prefix judge
						save_key = current_key
						level_rules = []
						self._get_all_dups(cursor, txn, level_rules)
						result += level_rules
						cursor.set_key(save_key)
					if current_key[0] < first_int:  # if current byte is less than first byte, break
						break
					if not cursor.prev():
						break

		return result

	def get_rules(self, url: str):
		rules = self.find(url)
		if len(rules) == 0:
			rules = self.find("__global__")  # used default global rules
		rulest = [msgpack.unpackb(r) for r in rules]
		rulest = self._merge_rules(rulest)
		rulest.sort(key=lambda x: x.get("Priority", 0), reverse=True)  # sort by Priority
		return rulest

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

	"""private methods"""

	def _make_hash(self, data: bytes) -> bytes:
		"""make hash of data, return 8 byte hash string"""
		return hashlib.blake2b(data, digest_size=8).digest()  # 8 byte hash

	def _get_all_dups(self, cursor, txn, result):
		"""get all index values with same key"""
		cursor.first_dup()  # move cursor to first dup
		for iv in cursor.iternext_dup():  # get all index values
			value = txn.get(iv[:16], db=self.rule_db)
			if value is not None:
				result.append(value)

	def _merge_rules(self, rules: list[dict]) -> list[dict]:
		"""merage rules (rules sort by [child, parent]).
		same Plugin, merge same config key and value (child override parent), if child value is None, delete parent config key
		:param rules: original rule list
		:return: merged rule list
		"""

		merged_map = {}

		for rule in reversed(rules):
			plugin = rule.get("Plugin")
			if not plugin:
				continue

			if plugin not in merged_map:  # first time meet this plugin, save it
				merged_map[plugin] = copy.deepcopy(rule)
			else:
				# meet this plugin again, merge it
				target_rule: dict = merged_map[plugin]
				# update Priority (child override parent)
				target_rule["Priority"] = rule.get("Priority", target_rule["Priority"])
				# merge config (child override parent)
				if "config" in rule:
					merge_dict_deep(target_rule.setdefault("config", {}), rule["config"])

		new_rules = list(merged_map.values())  # change map to list
		new_rules.sort(key=lambda x: x.get("Priority", 0))  # sort by Priority
		return new_rules

	"""async methods"""

	async def __aenter__(self):
		return self

	async def __aexit__(self, exc_type, exc_val, exc_tb):
		self.close()

	async def async_put(self, key: str, value: bytes, retry: int = 3):
		await asyncio.get_running_loop().run_in_executor(None, self.put, key, value, retry)

	async def async_get(self, key: str) -> list[bytes]:
		return await asyncio.get_running_loop().run_in_executor(None, self.get, key)

	async def async_remove(self, key: str, value: bytes = None) -> bool:
		return await asyncio.get_running_loop().run_in_executor(None, self.remove, key, value)

	async def async_find(self, url: str) -> list[bytes]:
		return await asyncio.get_running_loop().run_in_executor(None, self.find, url)

	async def async_get_rules(self, url: str):
		return await asyncio.get_running_loop().run_in_executor(None, self.get_rules, url)
