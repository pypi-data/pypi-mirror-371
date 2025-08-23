from typing import Optional
import aiomcache
import aiomcache.client
import hashlib
import logging


class Cache:
    def __init__(self, host: str, port: int) -> None:
        self._logger = logging.getLogger("cache")
        self._client = aiomcache.Client(host, port)

    async def set(self, key: str, data: bytes) -> None:
        try:
            await self._client.set(self._get_key(key), data)  # pylint: disable=no-value-for-parameter
            self._logger.info("Cached key %s", key)
        except aiomcache.ClientException as e:
            self._logger.info("Cache client exception: %s", e)
            return  # do nothing on cache failure
        except ConnectionResetError as e:
            self._logger.info("Cache conn reset: %s", e)
            return

    async def get(self, key: str) -> Optional[bytes]:
        try:
            response = await self._client.get(self._get_key(key))
            self._logger.info("Retrieved key %s", key)
            return response
        except aiomcache.ClientException as e:
            self._logger.info("Cache client exception: %s", e)
            return None
        except ConnectionResetError as e:
            self._logger.info("Cache conn reset: %s", e)
            return None

    def _get_key(self, key: str) -> bytes:
        encoded = hashlib.md5(key.encode("utf-8")).hexdigest()  # nosec
        return encoded.encode("utf-8")
