# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:expandtab
# Copyright 2017 juga (juga at riseup dot net), under MIT license.

import logging

from django.conf import settings
from django.core import serializers
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.mail.message import SafeMIMEText

from autocrypt.pgpymessage import gen_ac_header_dict

from .messagepgp import EmailMessagePGP

PE_CHOICES = (
    ("nopreference", _("nopreference")),
    ("mutual", _("mutual")),
    )

logger = logging.getLogger('ac')


class Account(models.Model):
    addr = models.EmailField(max_length=254)
    enabled = models.BooleanField()
    pe = models.CharField(max_length=20, choices=PE_CHOICES, default="",
                          help_text=_("prefer_encrypt"))
    skey = models.BinaryField(_('secret key'))
    pkey = models.BinaryField(_('public key'))

    def __str__(self):
        return self.addr

    @classmethod
    def serialize(self):
        serializers.serialize('json', Account.objects.all())

    @property
    def profiles(self):
        return self.profile_set.all()

    @property
    def profiles_str(self):
        return ", ".join([p.name for p in self.profiles])

    @property
    def out_emails(self):
        return self.out_email.all()


class Peer(models.Model):
    addr = models.EmailField(max_length=254)
    pe = models.CharField(max_length=20, choices=PE_CHOICES, default="",
                          help_text=_("prefer_encrypt"))
    pkey = models.BinaryField(_('public key'), editable=True)
    ls = models.DateTimeField(_('last seen'), auto_now=True, editable=True)
    ats = models.DateTimeField(_('autocrypt timestamp'), auto_now_add=True,
                               editable=True)
    gpk = models.BinaryField(_('gossip key'), editable=True,
                             null=True, blank=True)
    gts = models.DateTimeField(_('gossip timestamp'), null=True, blank=True)

    def __str__(self):
        return self.addr

    @classmethod
    def serialize(self):
        serializers.serialize('json', Peer.objects.all())

    @property
    def profiles(self):
        return self.profile_set.all()

    @property
    def profiles_str(self):
        return ", ".join([p.name for p in self.profiles])

    @property
    def in_emails(self):
        return self.in_email.all()


class Email(models.Model):
    date = models.DateTimeField(_('date'), auto_now_add=True)
    subject = models.CharField(_('subject'), max_length=255)
    body = models.TextField(_('body'))
    sender = models.ForeignKey(Account, related_name='out_email',
                               on_delete=models.SET_NULL,
                               null=True, blank=True, editable=True)
    recipients = models.ManyToManyField(Peer, related_name='in_email')
    mimepgp = None
    emailenc = models.TextField(_('mimepgp'), null=True, blank=True,
                                editable=True)

    def __str__(self):
        return "{0} {1}".format(self.subject[:30], self.sender.addr)

    class Meta:
        verbose_name = _('Email')
        verbose_name_plural = _("Emails")

    @classmethod
    def serialize(self):
        serializers.serialize('json', Email.objects.all())

    @property
    def profiles(self):
        return self.sender.profiles

    @property
    def profiles_str(self):
        return ", ".join([p.name for p in self.profiles])

    @property
    def sender_addr(self):
        return self.sender.addr

    @property
    def keydata(self):
        return self.sender.pkey

    @property
    def pe(self):
        return self.sender.pe

    @property
    def recipients_addr(self):
        return [r.addr for r in self.recipients.all()]

    @property
    def recipients_str(self):
        return ", ".join(self.recipients_addr)

    @property
    def ac_headers(self):
        return gen_ac_header_dict(self.sender_addr, self.keydata, self.pe)

    def encrypt(self):
        logger.info('Encrypting')
        mimetext = SafeMIMEText(self.body)
        logger.debug('sender addr %s', self.sender_addr)
        keyhandle = settings.P._get_keyhandle_from_addr(self.sender_addr)
        logger.debug('keyhandle %s', keyhandle)
        logger.debug('recipients addr %s', self.recipients_addr)
        encdata = settings.P.sign_encrypt(mimetext.as_bytes(), keyhandle,
                                          self.recipients_addr)

        self.mimepgp = EmailMessagePGP(self.subject, encdata, self.sender_addr,
                                       self.recipients_addr,
                                       headers=self.ac_headers)
        self.emailenc = self.mimepgp.message().as_string()

    def send(self):
        """Sends the email message."""
        logger.debug('Sending Email')
        self.mimepgp.send()

    def save(self, *args, **kwargs):
        logger.debug('Saving')
        self.encrypt()
        # TODO: here body could be removed
        super(Email, self).save(*args, **kwargs)
        self.send()


class Profile(models.Model):
    name = models.CharField(default="default", max_length=255)
    peers = models.ManyToManyField(Peer, verbose_name=_('peers'))
    account = models.ForeignKey(Account, verbose_name=_('accounts'))

    def __str__(self):
        return self.name

    @classmethod
    def serialize(self):
        serializers.serialize('json', Profile.objects.all())

    @property
    def in_emails(self):
        return [p.in_emails for p in self.peers.all()]

    @property
    def out_emails(self):
        return self.account.out_emails
