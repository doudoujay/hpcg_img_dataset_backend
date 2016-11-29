#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from main import app
from flask_cors import CORS
from config import DEFAULT_HOST, DEFAULT_PORT, DEBUG, THREADED


def runserver():
    port = int(os.environ.get('PORT', DEFAULT_PORT))
    app.run(host=DEFAULT_HOST, port=port, debug=DEBUG, threaded=THREADED)


if __name__ == '__main__':
    runserver()
