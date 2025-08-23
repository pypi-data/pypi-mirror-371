"""
AioHomematic: a Python 3 library to interact with HomeMatic and HomematicIP backends.

This package provides a high-level API to discover devices and channels, read and write
parameters (data points), receive events, and manage programs and system variables.

Key layers and responsibilities:
- aiohomematic.central: Orchestrates clients, caches, device creation and events.
- aiohomematic.client: Interface-specific clients (JSON-RPC/XML-RPC, Homegear) handling IO.
- aiohomematic.model: Data point abstraction for generic, hub, and calculated entities.
- aiohomematic.caches: Persistent and runtime caches for descriptions, values, and metadata.

Typical usage is to construct a CentralConfig, create a CentralUnit and start it, then
consume data points and events or issue write commands via the exposed API.
"""

from __future__ import annotations

import asyncio
import logging
import signal
import sys
import threading
from typing import Final

from aiohomematic import central as hmcu
from aiohomematic.const import VERSION

if sys.stdout.isatty():
    logging.basicConfig(level=logging.INFO)

__version__: Final = VERSION
_LOGGER: Final = logging.getLogger(__name__)


# pylint: disable=unused-argument
# noinspection PyUnusedLocal
def signal_handler(sig, frame):  # type: ignore[no-untyped-def]
    """Handle signal to shut down central."""
    _LOGGER.info("Got signal: %s. Shutting down central", str(sig))
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    for central in hmcu.CENTRAL_INSTANCES.values():
        asyncio.run_coroutine_threadsafe(central.stop(), asyncio.get_running_loop())


if threading.current_thread() is threading.main_thread() and sys.stdout.isatty():
    signal.signal(signal.SIGINT, signal_handler)
