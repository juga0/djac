# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:expandtab
# Copyright 2017 juga (juga at riseup dot net), under MIT license.

"""Extend Django email classes for MIME multipart/pgp-encrypted
type messages.
"""

__all__ = ['EmailMessageEnc', 'EmailMessagePGP']

from django.conf import settings
from django.core.mail.message import (
    EmailMessage, MIMEMixin,
    forbid_multi_line_headers, force_text,
    make_msgid, formatdate, DNS_NAME)
from emailpgp.mime.multipartpgp import MIMEMultipartPGP
from autocrypt.pgpymessage import gen_ac_header_dict


class SafeMIMEMultipart(MIMEMixin, MIMEMultipartPGP):

    def __init__(self, _data=None, _subtype='encrypted', boundary=None,
                 encoding=None, **_params):
        self.encoding = encoding
        MIMEMultipartPGP.__init__(self, _data, boundary, **_params)

    def __setitem__(self, name, val):
        name, val = forbid_multi_line_headers(name, val, self.encoding)
        MIMEMultipartPGP.__setitem__(self, name, val)


class EmailMessageEnc(EmailMessage):
    def message(self, msg):
        self.msg = msg


class EmailMessagePGP(EmailMessage):
    """A container for encrypted email information."""
    content_subtype = 'encrypted'
    mixed_subtype = ''

    def message(self):
        encoding = self.encoding or settings.DEFAULT_CHARSET
        msg = MIMEMultipartPGP(self.body)
        # FIXME: attachments
        # msg = self._create_message(msg)
        msg['Subject'] = self.subject
        msg['From'] = self.extra_headers.get('From', self.from_email)
        msg['To'] = self.extra_headers.get('To', ', '.join(map(force_text, self.to)))
        if self.cc:
            msg['Cc'] = ', '.join(map(force_text, self.cc))
        if self.reply_to:
            msg['Reply-To'] = self.extra_headers.get(
                'Reply-To', ', '.join(map(force_text, self.reply_to)))

        # Email header names are case-insensitive (RFC 2045), so we have to
        # accommodate that when doing comparisons.
        header_names = [key.lower() for key in self.extra_headers]
        if 'date' not in header_names:
            # formatdate() uses stdlib methods to format the date, which use
            # the stdlib/OS concept of a timezone, however, Django sets the
            # TZ environment variable based on the TIME_ZONE setting which
            # will get picked up by formatdate().
            msg['Date'] = formatdate(localtime=settings.EMAIL_USE_LOCALTIME)
        if 'message-id' not in header_names:
            # Use cached DNS_NAME for performance
            msg['Message-ID'] = make_msgid(domain=DNS_NAME)
        for name, value in self.extra_headers.items():
            # From and To are already handled
            if name.lower() in ('from', 'to'):
                continue
            msg[name] = value
        return msg


def EmailMessagePGPAC(EmailMessagePGP):

    def __init__(self, subject='', body='', from_email=None, to=None, bcc=None,
                 connection=None, attachments=None, headers=None, cc=None,
                 reply_to=None, keydata=None, pe=None):
        super(EmailMessagePGPAC, self).__init__(
            subject, body, from_email, to, bcc, connection, attachments,
            headers, cc, reply_to)
        self.extra_headers = self.extra_headers.update(
            gen_ac_header_dict(to, keydata, pe))
