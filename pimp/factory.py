# -*- coding: utf-8 -*-
"""
    overholt.factory
    ~~~~~~~~~~~~~~~~

    overholt factory module
"""

import os



from celery import Celery
from .helpers import Flask
from flask_security import SQLAlchemyUserDatastore, Security
from flask.ext.social import Social
from flask.ext.social.datastore import SQLAlchemyConnectionDatastore

from .core import db, mail, py_mongo, security
from .helpers import register_blueprints
from .middleware import HTTPMethodOverrideMiddleware
from models import User, Role, Connection






def create_app(package_name, package_path, settings_override=None,
               register_security_blueprint=True):
    """Returns a :class:`Flask` application instance configured with common
    functionality for the Overholt platform.

    :param package_name: application package name
    :param package_path: application package path
    :param settings_override: a dictionary of settings to override
    :param register_security_blueprint: flag to specify if the Flask-Security
                                        Blueprint should be registered. Defaults
                                        to `True`.
    """
    app = Flask(package_name, instance_relative_config=True)
    app.config.from_yaml(app.root_path)
    app.config.from_heroku()
    if app.config['ENVIRONMENT'] == "development":
        app.debug = True


    db.init_app(app)
    mail.init_app(app)
    #security.init_app(app, SQLAlchemyUserDatastore(db, User, Role),
    #                  register_blueprint=register_security_blueprint)
    py_mongo.init_app(app)
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    Security(app, user_datastore,  register_blueprint=register_security_blueprint)
    Social(app, SQLAlchemyConnectionDatastore(db, Connection))
    register_blueprints(app, package_name, package_path)
    app.wsgi_app = HTTPMethodOverrideMiddleware(app.wsgi_app)

    return app


def create_celery_app(app=None):
    app = app or create_app('pimp', os.path.dirname(__file__))
    celery = Celery(__name__, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery
