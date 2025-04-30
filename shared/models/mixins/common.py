"""
Custom Django Models and Mixins

This module contains custom Django models and mixins
for handling timestamps.
"""

import os

from django.db import models
from django.utils.translation import gettext_lazy as _


class CreatedTimeStamp(models.Model):
    """
    A mixin for adding created field to a Django model.
    """

    created = models.DateTimeField(_("Created Time"), auto_now_add=True)

    class Meta:
        abstract = True


class TimeStampMixin(CreatedTimeStamp):
    """
    A mixin for adding timestamp fields to a Django model.

    Attributes:
        created (DateTimeField): The timestamp for when the object was created.
        modified (DateTimeField): The timestamp for when the object was last modified.
    """

    modified = models.DateTimeField(_("Modified Time"), auto_now=True)

    class Meta:
        abstract = True
