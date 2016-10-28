# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from django.conf import settings


class Settings(object):

    defaults = {
        'MODE': 'once'
    }

    def get_setting(self, key):
        try:
            return settings.PERF_REC[key]
        except (AttributeError, IndexError):
            return self.defaults.get(key, None)

    @property
    def MODE(self):
        return self.get_setting('MODE')


perf_rec_settings = Settings()
