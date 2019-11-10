#!/usr/bin/env python
#-*- coding:utf-8 -*-

#
# This module imports the communication sub modules
# during initialization. Not sure if I'm violating
# best practices..
#

import os
from logger import logger
from importlib import import_module

logger = logger()

class SMS(object):
    def __init__(self, *args, **kwargs):
        """
        Class to send sms using the provider of your choice
        To use:
        with SMS() as sms:
            sms.send_sms(from_number, to_number, text, medial_url)
        """
        try:
            # If you have multiple api calls/ classes/ modules
            # add them here with any logic if you want to implement
            # For example, if you have twilio, quic and nexmo accounts
            # Import their classes and add round-robin or some other logic for
            # send_sms() method so that the load for outgoing text
            # is distributed and your calling code implementation doesn't
            # have to change
            # e.g.
            # mysmsclients = []
            # self.sms_client = random.choice(mysmsclients)
            self.sms_client = Twilio(*args, **kwargs)
        except ModuleNotFoundError:
            logger.warning('Twilio module not found')
            return None

    def __enter__(self, *args):
        return self

    def __exit__(self, *args):
        # Any cleanup step for your class/ module should go here
        pass
    
    def send_sms(self, **kwargs):
        try:
            from_number = kwargs.get('from_number')
            to_number = kwargs.get('to_number')
            text = kwargs.get('text')
            media_url = kwargs.get('media_url')
            self.sms_client.send_text(from_number, to_number, text, media_url)
        except Exception as ex:
            # Anything goes wrong while sending text, log and move on.
            logger.error("Could not send sms: \n{}".format(ex))

class Twilio(object):
    def __init__(self, *args, **kwargs):
        from twilio.rest import Client
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        if account_sid and auth_token:
            self.twilio_client = Client(account_sid, auth_token)
        else:
            logger.error("TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN is not set")
            return None

    def send_text(self, from_number, to_number, text, media_url=None):
        """
        Send SMS text to a "local" phone number.

        Parameters:
        ----------
        from_number: str
            local twilio number registered on the account in E.164 format
            https://en.wikipedia.org/wiki/E.164
        to_number: str
            local number to send tex to
        text: str
            body of the sms. In text format
        media_url: list, Optional
            list of multimedia objects (url) to be sent. Should be publicly accessible urls

        Returns:
        -------
        status: tuple
            Tuple of message sid and message status
        """
        message = self.twilio_client.messages.create(from_=from_number,
                                                     to=to_number,
                                                     body=text,
                                                     media_url=media_url,)
        logger.info("Sent message via Twilio \nMessageSID: {}\nMessageStatus: {}".format(message.sid, message.status))
