# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:expandtab
# Copyright 2017 juga (juga at riseup dot net), under MIT license.

import logging
from django.contrib import admin

from .models import (Account, Peer, Profile, Email)

logger = logging.getLogger('ac')


class OutEmailInline(admin.StackedInline):
    model = Email
    extra = 0


class ProfileInline(admin.TabularInline):
    model = Profile
    extra = 0


class InEmailsInline(admin.TabularInline):
    model = Email.recipients.through
    extra = 0


class ProfilePeerInline(admin.TabularInline):
    model = Profile.peers.through
    extra = 0


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'account')


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipients_str', 'subject', 'date',
                    'profiles_str')

    # recipients_str.short_description = 'Recipients'

    # inlines = (ProfilePeerInline,)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('addr', 'enabled', 'pe', 'profiles_str')

    inlines = [ProfileInline, OutEmailInline]


@admin.register(Peer)
class PeerAdmin(admin.ModelAdmin):
    list_display = ('addr', 'pe', 'ls', 'ats', 'gts', 'profiles_str')

    # fields = ('addr', 'pe', 'pkey', 'ls', 'ats', 'gpk', 'gts')

    inlines = (InEmailsInline, ProfilePeerInline)
