#!/usr/bin/python

import sys
import logging

logger = logging.getLogger('user_func1')
hdlr = logging.FileHandler('/home/ash/user_func1.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO)

logger.info(str(sys.argv))