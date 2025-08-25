from __future__ import annotations

import logging

import wrapt

from odoo import http
from odoo.http import request

_logger = logging.getLogger("odoo.session.REDIS")


def patch_function(module: str, name: str, enabled: bool = True):
    _logger.info("Activate monkey patch on %s#%s -> %s", module, name, enabled)
    if not enabled:

        def pass_wrapper(wrapper):
            return wrapper

        return pass_wrapper
    return wrapt.patch_function_wrapper(module, name)


@patch_function("odoo.addons.base", "models.ir_http.IrHttp._authenticate")
def _patch_from_attachment(wrapped, instance, args, kwargs):
    if (
        hasattr(http.root.session_store, "update_expiration")
        and request
        and request.session
        and request.session.uid
        and not request.env["res.users"].browse(request.session.uid)._is_public()
    ):
        http.root.session_store.update_expiration(request.session)
    return wrapped(*args, **kwargs)
