#!/usr/bin/env python3
import sys
import logging

from terrestrial import app


log = logging.getLogger('worker')
log_format = '[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s'
logging.basicConfig(level=logging.INFO,format=log_format)


if __name__ == '__main__':
    argv = ['worker'].extend(sys.argv[1:])
    app.worker_main(argv)
