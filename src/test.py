import logging
from cchesslib.chessman import *
from util.logger import logger
import time

while True:
    logger.setLevel(logging.DEBUG)
    logger.debug("debug")
    logger.info("info")
    logger.warning("warning")
    logger.error("error")
    time.sleep(1)
