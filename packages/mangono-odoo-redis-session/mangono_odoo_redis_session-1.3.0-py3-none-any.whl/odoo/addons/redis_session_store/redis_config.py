from __future__ import annotations

import dataclasses
import os

import redis

DEFAULT_SESSION_TIMEOUT = 60 * 60 * 24 * 3  # 3 days in seconds
DEFAULT_SESSION_TIMEOUT_ANONYMOUS = 60 * 2  # 2 minutes in seconds
DEFAULT_SESSION_TIMEOUT_ON_INACTIVITY = "True"
DEFAULT_SESSION_TIMEOUT_IGNORED_URLS = ["/longpolling", "/calendar/notify"]


@dataclasses.dataclass
class RedisConfig:
    host: str | None = None
    port: int | None = None
    prefix: str | None = None
    password: str | None = None
    url: str | None = None
    expiration: int | None = None
    anon_expiration: int | None = None
    db: str | None = None
    timeout_on_inactivity: bool | None = None
    ignored_urls: list[str] | None = None

    def connect(self) -> redis.Redis:
        """
        Return the connection to the Redis server.
        If `self.url` is filled, then `url` all other connection info are exclude.

        expiration, and anon_expiration are not passed to the connection.

        :return: A connection to the Redis server.
        """
        if self.url:
            return redis.Redis.from_url(self.url)
        return redis.Redis(
            host=self.host,
            port=self.port,
            db=int(self.db or "0"),
            password=self.password,
        )

    @classmethod
    def create_config(cls, odoo_config=None) -> RedisConfig:
        """
        Create a RedisConfig instance for each call. Take the config inside `odoo_config` if filled in.
        The config should be inside the misc section named `redis_sessions_store`.
        Otherwise, create a new RedisConfig instance from the `os.environ` variable.

        :param odoo_config: The optional odoo.tools.config instance
        :return: A config class to connect
        """
        _config_data = odoo_config.misc.get("redis_sessions_store", {})
        ignored_urls = DEFAULT_SESSION_TIMEOUT_IGNORED_URLS
        additional_urls = os.environ.get(
            "ODOO_SESSION_REDIS_TIMEOUT_IGNORED_URLS",
            _config_data.get("ignored_urls", ""),
        )
        if additional_urls:
            ignored_urls += additional_urls.split(",")
        return cls(
            **{
                "host": os.environ.get("REDIS_HOST", _config_data.get("host", "localhost")),
                "port": int(os.environ.get("REDIS_PORT", _config_data.get("port", 6379))),
                "prefix": os.environ.get("REDIS_PREFIX", _config_data.get("prefix")),
                "url": os.environ.get("REDIS_URL", _config_data.get("url")),
                "password": os.environ.get("REDIS_PASSWORD", _config_data.get("password")),
                "expiration": int(
                    os.environ.get(
                        "ODOO_SESSION_REDIS_EXPIRATION", _config_data.get("expiration", DEFAULT_SESSION_TIMEOUT)
                    )
                ),
                "anon_expiration": int(
                    os.environ.get(
                        "ODOO_SESSION_REDIS_EXPIRATION_ANONYMOUS",
                        _config_data.get("anon_expiration", DEFAULT_SESSION_TIMEOUT_ANONYMOUS),
                    )
                ),
                "timeout_on_inactivity": os.environ.get(
                    "ODOO_SESSION_REDIS_TIMEOUT_ON_INACTIVITY",
                    _config_data.get("timeout_on_inactivity", DEFAULT_SESSION_TIMEOUT_ON_INACTIVITY),
                ).lower()
                in ("true", "1", "t"),
                "ignored_urls": ignored_urls,
            }
        )
