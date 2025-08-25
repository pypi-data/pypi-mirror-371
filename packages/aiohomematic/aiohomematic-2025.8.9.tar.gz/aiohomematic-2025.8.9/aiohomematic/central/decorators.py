"""Decorators for central used within aiohomematic."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from datetime import datetime
from functools import wraps
import inspect
import logging
from typing import Any, Final, cast

from aiohomematic import central as hmcu, client as hmcl
from aiohomematic.central import xml_rpc_server as xmlrpc
from aiohomematic.const import BackendSystemEvent
from aiohomematic.exceptions import AioHomematicException
from aiohomematic.support import extract_exc_args

_LOGGER: Final = logging.getLogger(__name__)
_INTERFACE_ID: Final = "interface_id"


def callback_backend_system(system_event: BackendSystemEvent) -> Callable:
    """Check if backend_system_callback is set and call it AFTER original function."""

    def decorator_backend_system_callback[**P, R](
        func: Callable[P, R | Awaitable[R]],
    ) -> Callable[P, R | Awaitable[R]]:
        """Decorate callback system events."""

        @wraps(func)
        async def async_wrapper_backend_system_callback(*args: P.args, **kwargs: P.kwargs) -> R:
            """Wrap async callback system events."""
            return_value = cast(R, await func(*args, **kwargs))  # type: ignore[misc]
            await _exec_backend_system_callback(*args, **kwargs)
            return return_value

        @wraps(func)
        def wrapper_backend_system_callback(*args: P.args, **kwargs: P.kwargs) -> R:
            """Wrap callback system events."""
            return_value = cast(R, func(*args, **kwargs))
            try:
                unit = args[0]
                central: hmcu.CentralUnit | None = None
                if isinstance(unit, hmcu.CentralUnit):
                    central = unit
                if central is None and isinstance(unit, xmlrpc.RPCFunctions):
                    central = unit.get_central(interface_id=str(args[1]))
                if central:
                    central.looper.create_task(
                        _exec_backend_system_callback(*args, **kwargs),
                        name="wrapper_backend_system_callback",
                    )
            except Exception as exc:
                _LOGGER.warning(
                    "EXEC_BACKEND_SYSTEM_CALLBACK failed: Problem with identifying central: %s",
                    extract_exc_args(exc=exc),
                )
            return return_value

        async def _exec_backend_system_callback(*args: Any, **kwargs: Any) -> None:
            """Execute the callback for a system event."""

            if not ((len(args) > 1 and not kwargs) or (len(args) == 1 and kwargs)):
                _LOGGER.warning("EXEC_BACKEND_SYSTEM_CALLBACK failed: *args not supported for callback_system_event")
            try:
                args = args[1:]
                interface_id: str = args[0] if len(args) > 0 else str(kwargs[_INTERFACE_ID])
                if client := hmcl.get_client(interface_id=interface_id):
                    client.modified_at = datetime.now()
                    client.central.fire_backend_system_callback(system_event=system_event, **kwargs)
            except Exception as exc:  # pragma: no cover
                _LOGGER.warning(
                    "EXEC_BACKEND_SYSTEM_CALLBACK failed: Unable to reduce kwargs for backend_system_callback"
                )
                raise AioHomematicException(
                    f"args-exception backend_system_callback [{extract_exc_args(exc=exc)}]"
                ) from exc

        if inspect.iscoroutinefunction(func):
            return async_wrapper_backend_system_callback
        return wrapper_backend_system_callback

    return decorator_backend_system_callback


def callback_event[**P, R](
    func: Callable[P, R],
) -> Callable:
    """Check if event_callback is set and call it AFTER original function."""

    @wraps(func)
    async def async_wrapper_event_callback(*args: P.args, **kwargs: P.kwargs) -> R:
        """Wrap callback events."""
        return_value = cast(R, await func(*args, **kwargs))  # type: ignore[misc]
        _exec_event_callback(*args, **kwargs)
        return return_value

    def _exec_event_callback(*args: Any, **kwargs: Any) -> None:
        """Execute the callback for a data_point event."""
        try:
            args = args[1:]
            interface_id: str = args[0] if len(args) > 1 else str(kwargs[_INTERFACE_ID])
            if client := hmcl.get_client(interface_id=interface_id):
                client.modified_at = datetime.now()
                client.central.fire_backend_parameter_callback(*args, **kwargs)
        except Exception as exc:  # pragma: no cover
            _LOGGER.warning("EXEC_DATA_POINT_EVENT_CALLBACK failed: Unable to reduce kwargs for event_callback")
            raise AioHomematicException(f"args-exception event_callback [{extract_exc_args(exc=exc)}]") from exc

    return async_wrapper_event_callback
