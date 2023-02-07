from __future__ import annotations

import sys
from typing import Any

from django.conf import settings

if sys.version_info >= (3, 8):
    from typing import Literal

    ModeType = Literal["all", "none", "once", "overwrite"]
else:
    ModeType = str


class Settings:
    defaults = {"HIDE_COLUMNS": True, "MODE": "once"}

    def get_setting(self, key: str) -> Any:
        try:
            return settings.PERF_REC[key]
        except (AttributeError, KeyError):
            return self.defaults.get(key, None)

    @property
    def HIDE_COLUMNS(self) -> bool:
        return bool(self.get_setting("HIDE_COLUMNS"))

    @property
    def MODE(self) -> ModeType:
        value = self.get_setting("MODE")
        assert value in ("all", "none", "once", "overwrite")
        return value  # type: ignore [no-any-return]


perf_rec_settings = Settings()
