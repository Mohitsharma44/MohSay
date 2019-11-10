#!/usr/bin/env python

import os
import sys
import json
import pika
from logger import logger
from sms import SMS

host = os.environ.get('RABBIT_HOST')
port = os.environ.get('RABBIT_PORT', '5672')
vhost = os.environ.get('RABBIT_VHOST', '/')
queue = os.environ.get('RABBIT_QUEUE')
username = os.environ.get('RABBIT_USER')
password = os.environ.get('RABBIT_PASS')

logger = logger()

def callback(ch, method, properties, body):
    try:
        msg = json.loads(body)
        with SMS() as sms:
            sms.send_sms(**msg)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as ex:
        logger.critical("Error consuming message: {}".format(ex))

if __name__ == "__main__":
    logger.info("Starting up")
    try:
        credentials = pika.PlainCredentials(username, password)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host, port, vhost, credentials))
        channel = connection.channel()
        channel.queue_declare(queue=queue, durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=queue, on_message_callback=callback)
        channel.start_consuming()
    except Exception as ex:
        logger.critical("Exception in main loop: {}".format(ex))
        logger.critical("Exiting")
        sys.exit(2)
