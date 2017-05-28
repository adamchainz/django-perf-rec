#!/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import codecs
import os
import re

from setuptools import find_packages, setup


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    with codecs.open(os.path.join(package, '__init__.py'), 'r', 'utf-8') as fp:
        init_py = fp.read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


version = get_version('django_perf_rec')


with codecs.open('README.rst', 'r', 'utf-8') as readme_file:
    readme = readme_file.read()

with codecs.open('HISTORY.rst', 'r', 'utf-8') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

setup(
    name='django-perf-rec',
    version=version,
    description="Keep detailed records of the performance of your Django "
                "code.",
    long_description=readme + '\n\n' + history,
    author='YPlan',
    author_email='adam@yplanapp.com',
    url='https://github.com/YPlan/django-perf-rec',
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    install_requires=[
        'Django',
        'patchy',
        'PyYAML',
        'six',
        'sqlparse>=0.2.0',
    ],
    license='MIT',
    zip_safe=False,
    keywords='Django',
    entry_points={
        'pytest11': ['django_perf_rec = django_perf_rec.pytest_plugin'],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
