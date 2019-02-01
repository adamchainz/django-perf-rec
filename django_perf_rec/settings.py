from django.conf import settings


class Settings(object):

    defaults = {
        'HIDE_COLUMNS': True,
        'MODE': 'once',
    }

    def get_setting(self, key):
        try:
            return settings.PERF_REC[key]
        except (AttributeError, KeyError):
            return self.defaults.get(key, None)

    @property
    def HIDE_COLUMNS(self):
        return self.get_setting('HIDE_COLUMNS')

    @property
    def MODE(self):
        return self.get_setting('MODE')


perf_rec_settings = Settings()
