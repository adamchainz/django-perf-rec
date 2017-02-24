# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=32, unique=True)
    age = models.IntegerField()


class Book(models.Model):
    title = models.CharField(max_length=128)
    author = models.ForeignKey(Author)


class Award(models.Model):
    name = models.CharField(max_length=128)
    author = models.ForeignKey(Author)


class Contract(models.Model):
    amount = models.IntegerField()
    author = models.ManyToManyField(Author)
