#!/usr/bin/python3

import socket
import time
import datetime
import logging

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('0.0.0.0', 10086))
except Exception as e:
    logging.fatal("got exception while create socket or bind")
    exit(-1)

try:
    ip_addr = socket.gethostbyname('www.baidu.com')
except Exception as e:
    logging.error("gethostbyname failed!")
    exit(-1)

while True:
    current_timestamp = str(datetime.datetime.now())
    try:
        logging.debug("sendto begin")
        sendto_ret = s.sendto(('hello udp, %s' % current_timestamp).encode('utf-8'), (ip_addr, 11452))
        logging.debug("sendto end, ret = [%d]" % sendto_ret)
    except Exception as e:
        logging.warn("got exception while sendto")
        print(e)
        pass
    time.sleep(0.5)