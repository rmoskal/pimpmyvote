# -*- coding: utf-8 -*-
"""
    wsgi
    ~~~~

    pimp wsgi module
"""
import os

from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware

from pimp import frontend

app = frontend.create_app()
application = DispatcherMiddleware(app)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    run_simple('0.0.0.0', port, application, use_reloader=app.debug, use_debugger=app.debug)