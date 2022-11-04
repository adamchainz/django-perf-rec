from __future__ import annotations

from typing import Dict
from typing import List
from typing import Union

PerformanceRecordItem = Dict[str, Union[str, List[str]]]
PerformanceRecord = List[PerformanceRecordItem]
