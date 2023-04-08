#!/usr/bin/python3

import socket
import time
import logging
import signal

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('0.0.0.0', 11452))
except Exception as e:
    logging.fatal("got exception while create socket or bind")
    exit(-1)
print(s)

while True:
    try:
        logging.debug("recvfrom begin")
        buf = s.recvfrom(1024)
        print(buf)
        logging.debug("recvfrom end, ret = [%d]" % len(buf))
    except Exception as e:
        logging.warn("got exception while recvfrom")
        print(e)
    time.sleep(0.5)

