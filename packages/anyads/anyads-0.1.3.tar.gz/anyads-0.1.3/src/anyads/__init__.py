# src/anyads/__init__.py

from .client import PollingSDK, init, get_sdk_instance
from .exceptions import AnyAdsException, InitializationError, APIError


__all__ = [
    "PollingSDK",
    "init",
    "get_sdk_instance",
    "AnyAdsException",
    "InitializationError",
    "APIError",
    "integrations",
]

import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())