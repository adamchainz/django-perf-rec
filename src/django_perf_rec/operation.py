from django.conf import settings

from django_perf_rec.utils import sorted_names


class Operation:
    def __init__(self, alias, query, traceback):
        self.alias = alias
        self.query = query
        self.traceback = traceback

    def __eq__(self, other):
        return (
            isinstance(other, type(self))
            and self.alias == other.alias
            and self.query == other.query
            and self.traceback == other.traceback
        )


class AllSourceRecorder:
    """
    Launches Recorders on all the active sources
    """

    sources_setting = None
    recorder_class = None

    def __init__(self, callback):
        self.callback = callback

    def __enter__(self):
        self.recorders = []
        for name in sorted_names(getattr(settings, self.sources_setting).keys()):
            recorder = self.recorder_class(name, self.callback)
            recorder.__enter__()
            self.recorders.append(recorder)

    def __exit__(self, type_, value, traceback):
        for recorder in reversed(self.recorders):
            recorder.__exit__(type_, value, traceback)
        self.recorders = []
