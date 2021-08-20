import difflib
import inspect
from collections import namedtuple
from types import FrameType
from typing import Iterable, List, Optional

from django_perf_rec import _HAVE_PYTEST
from django_perf_rec.types import PerformanceRecord

TestDetails = namedtuple("TestDetails", ["file_path", "class_name", "test_name"])


def current_test() -> TestDetails:
    """
    Use a little harmless stack inspection to determine the test that is
    currently running.
    """
    frame = inspect.currentframe()
    assert frame is not None
    try:
        while True:
            details = _get_details_from_test_function(
                frame
            ) or _get_details_from_pytest_request(frame)

            if details is not None:
                return details

            # Next frame
            frame = frame.f_back
            if frame is None:
                break

        raise RuntimeError("Could not automatically determine the test name.")
    finally:
        # Always delete frame references to help garbage collector
        del frame


def _get_details_from_test_function(frame: FrameType) -> Optional[TestDetails]:
    if not frame.f_code.co_name.startswith("test_"):
        return None

    file_path = frame.f_globals["__file__"]

    # May be a pytest function test so we can't assume 'self' exists
    its_self = frame.f_locals.get("self", None)
    if its_self is None:
        class_name = None
    else:
        class_name = its_self.__class__.__name__

    test_name = frame.f_code.co_name

    return TestDetails(file_path=file_path, class_name=class_name, test_name=test_name)


def _get_details_from_pytest_request(frame: FrameType) -> Optional[TestDetails]:
    if not _HAVE_PYTEST:
        return None

    request = frame.f_locals.get("request", None)
    if request is None:
        return None

    if request.cls is not None:
        class_name = request.cls.__name__
    else:
        class_name = None

    return TestDetails(
        file_path=request.fspath.strpath,
        class_name=class_name,
        test_name=request.function.__name__,
    )


def sorted_names(names: Iterable[str]) -> List[str]:
    """
    Sort a list of names but keep the word 'default' first if it's there.
    """
    names = list(names)

    have_default = False
    if "default" in names:
        names.remove("default")
        have_default = True

    sorted_names = sorted(names)

    if have_default:
        sorted_names = ["default"] + sorted_names

    return sorted_names


def record_diff(old: PerformanceRecord, new: PerformanceRecord) -> str:
    """
    Generate a human-readable diff of two performance records.
    """
    return "\n".join(
        difflib.ndiff(
            [f"{k}: {v}" for op in old for k, v in op.items()],
            [f"{k}: {v}" for op in new for k, v in op.items()],
        )
    )
