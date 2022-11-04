from __future__ import annotations

import inspect
import re
import traceback
from collections.abc import Collection
from functools import wraps
from types import MethodType
from types import TracebackType
from typing import Any
from typing import Callable
from typing import cast
from typing import Collection as TypingCollection
from typing import Pattern
from typing import TypeVar

from django.core.cache import caches
from django.core.cache import DEFAULT_CACHE_ALIAS

from django_perf_rec.operation import AllSourceRecorder
from django_perf_rec.operation import BaseRecorder
from django_perf_rec.operation import Operation


class CacheOp(Operation):
    def __init__(
        self,
        alias: str,
        operation: str,
        key_or_keys: str | TypingCollection[str],
        traceback: traceback.StackSummary,
    ):
        self.alias = alias
        self.operation = operation
        cleaned_key_or_keys: str | TypingCollection[str]
        if isinstance(key_or_keys, str):
            cleaned_key_or_keys = self.clean_key(key_or_keys)
        elif isinstance(key_or_keys, Collection):
            cleaned_key_or_keys = sorted(self.clean_key(k) for k in key_or_keys)
        else:
            raise ValueError("key_or_keys must be a string or collection")

        super().__init__(alias, cleaned_key_or_keys, traceback)

    @classmethod
    def clean_key(cls, key: str) -> str:
        """
        Replace things that look like variables with a '#' so tests aren't
        affected by random variables
        """
        for var_re in cls.VARIABLE_RES:
            key = var_re.sub("#", key)
        return key

    VARIABLE_RES: tuple[Pattern[str], ...] = (
        # Django session keys for 'cache' backend
        re.compile(r"(?<=django\.contrib\.sessions\.cache)[0-9a-z]{32}\b"),
        # Django session keys for 'cached_db' backend
        re.compile(r"(?<=django\.contrib\.sessions\.cached_db)[0-9a-z]{32}\b"),
        # Long random hashes
        re.compile(r"\b[0-9a-f]{32}\b"),
        # UUIDs
        re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"),
        # Integers
        re.compile(r"\d+"),
    )

    def __eq__(self, other: Any) -> bool:
        return super().__eq__(other) and self.operation == other.operation

    @property
    def name(self) -> str:
        name_parts = ["cache"]
        if self.alias != DEFAULT_CACHE_ALIAS:
            name_parts.append(self.alias)
        name_parts.append(self.operation)
        return "|".join(name_parts)


CacheFunc = TypeVar("CacheFunc", bound=Callable[..., Any])


class CacheRecorder(BaseRecorder):
    """
    Monkey patches a cache class to call 'callback' on every operation it calls
    """

    def __enter__(self) -> None:
        cache = caches[self.alias]

        def call_callback(func: CacheFunc) -> CacheFunc:
            alias = self.alias
            callback = self.callback

            @wraps(func)
            def inner(self: Any, *args: Any, **kwargs: Any) -> Any:
                # Ignore operations from the cache class calling itself

                # Get the self of the parent via stack inspection
                frame = inspect.currentframe()
                assert frame is not None
                try:
                    frame = frame.f_back
                    is_internal_call = (
                        frame is not None and frame.f_locals.get("self", None) is self
                    )
                finally:
                    # Always delete frame references to help garbage collector
                    del frame

                if not is_internal_call:
                    key_or_keys = args[0]
                    callback(
                        CacheOp(
                            alias=alias,
                            operation=str(func.__name__),
                            key_or_keys=key_or_keys,
                            traceback=traceback.extract_stack(),
                        )
                    )

                return func(*args, **kwargs)

            return cast(CacheFunc, inner)

        self.orig_methods = {name: getattr(cache, name) for name in self.cache_methods}
        for name in self.cache_methods:
            orig_method = self.orig_methods[name]
            setattr(cache, name, MethodType(call_callback(orig_method), cache))

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        exc_traceback: TracebackType | None,
    ) -> None:
        cache = caches[self.alias]
        for name in self.cache_methods:
            setattr(cache, name, self.orig_methods[name])
        del self.orig_methods

    cache_methods = (
        "add",
        "decr",
        "delete",
        "delete_many",
        "get",
        "get_many",
        "get_or_set",
        "incr",
        "set",
        "set_many",
    )


class AllCacheRecorder(AllSourceRecorder):
    """
    Launches CacheRecorders on all the active caches
    """

    sources_setting = "CACHES"
    recorder_class = CacheRecorder
