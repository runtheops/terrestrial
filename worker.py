#!/usr/bin/env python3
import sys

from terrestrial import app


if __name__ == '__main__':
    argv = ['worker'].extend(sys.argv[1:])
    app.worker_main(argv)
