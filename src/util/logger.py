import logging
import logging.handlers

LOG_FORMAT = '[%(asctime)s][%(levelname)s] %(message)s'
DATE_FORMAT = '%Y/%m/%d %H:%M:%S'

logger = logging.getLogger('chess')
formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

fh = logging.handlers.RotatingFileHandler('../log/all.log',
                                          backupCount=10,
                                          maxBytes=2**20)
fh.setFormatter(formatter)
logger.addHandler(fh)

logger.setLevel(level=logging.DEBUG)
