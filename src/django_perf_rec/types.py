from __future__ import annotations

from typing import Union

PerformanceRecordItem = dict[str, Union[str, list[str]]]
PerformanceRecord = list[PerformanceRecordItem]
