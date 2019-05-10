#!/usr/bin/env python3
import logging

from terrestrial import api


log = logging.getLogger('api')
log_format = '[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s'
logging.basicConfig(level=logging.INFO,format=log_format)


if __name__ == '__main__':
    api.run()
