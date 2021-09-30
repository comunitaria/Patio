# -*- coding: utf-8 -*-
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from decimal import Decimal
import time


class Community(models.Model):
    nif = models.CharField(max_length=350, default="", blank=True)
    homes_count = models.IntegerField(default=0)
    stores_count = models.IntegerField(default=0)
    garages_count = models.IntegerField(default=0)
    community_name = models.CharField(max_length=100, blank=True, null=True, default="")
    community_address = models.CharField(max_length=150, blank=True, null=True, default="")

    president = models.CharField(max_length=100, default="", blank=True)
    secretary = models.CharField(max_length=100, default="", blank=True)


    def __str__(self):
        return "Community: %s, %s" % (self.community_address, self.nif)


class UserCommunity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='communities')
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='users')
    administrator = models.BooleanField(default=False)
    phone_1 = models.CharField(max_length=20)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def full_name(self):
        return self.user.first_name + ' ' + self.user.last_name

    class Meta:
        unique_together = ('user', 'community')

