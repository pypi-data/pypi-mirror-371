# Odoo Session inside Redis

Use redis to store odoo cookie session.

Inspired by :

https://github.com/odoo/odoo-extra/commit/99265410bf396fc476c0a4502a44549a1dd29ef2

This gist https://gist.github.com/carlopires/1451947

This module https://github.com/Smile-SA/odoo_addons/commit/d90e23f6fbc078beb0cb14080a2b18de332200ef

And this module https://github.com/camptocamp/odoo-cloud-platform/tree/16.0/session_redis

## Install

```shell
pip install mangono-odoo-redis-session
```

## Config

Configuration is done through environment variables. Alternatively, you can use a config parameter under `[redis_sessions_store]`. Environment variable have higher priority than config parameter.

`ENV_VARIABLE_NAME = default` | `config_parameter`

### Redis connection

`REDIS_HOST = None` | `host` – Redis host.

`REDIS_PORT = None` | `port` – Redis host port.

`REDIS_PREFIX = None` | `prefix` – Prefix for Redis keys.

`REDIS_URL = None` | `url` – Alternative connection through url.

`REDIS_PASSWORD = None` | `password` – Redis password.

### Session TTL parameters

`ODOO_SESSION_REDIS_EXPIRATION = 259200` | `expiration` –  Logged session TTL in seconds.

`ODOO_SESSION_REDIS_EXPIRATION_ANONYMOUS = 120` | `anon_expiration` – Anonymous session TTL in seconds.

`ODOO_SESSION_REDIS_TIMEOUT_ON_INACTIVITY = "True"` | `timeout_on_inactivity` – `"true" | "1" | "t"` will evaluate to `True` (case-insensitive), all other values will evaluate to `False` – Whether user activity should reset session TTL or not. If false, session will have a fixed expiration set on creation.

`ODOO_SESSION_REDIS_TIMEOUT_IGNORED_URLS = "/longpolling,/calendar/notify"` | `ignored_urls` – Comma separated list of string matching starts of endpoints that won't update session TTL on access. Has no effect when in fixed TTL mode. Note that the default value is not overridable and will always be added.

## Known issues

On fixed expiry time , refreshing the page still refresh TTL.

See doc in https://atlas.docs.mangono.io/redis-session