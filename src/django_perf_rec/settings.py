from __future__ import annotations

from typing import Any, Literal

from django.conf import settings


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
    def MODE(self) -> Literal["all", "none", "once", "overwrite"]:
        value = self.get_setting("MODE")
        assert value in ("all", "none", "once", "overwrite")
        return value  # type: ignore [no-any-return]


perf_rec_settings = Settings()
