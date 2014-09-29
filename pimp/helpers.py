# -*- coding: utf-8 -*-
"""
    pimp.helpers
    ~~~~~~~~~~~~~~~~

    pimp helpers module
"""

import pkgutil
import importlib
import os
from urlparse import urlparse
import yaml

from flask import Blueprint
from flask.json import JSONEncoder as BaseJSONEncoder
from sqlalchemy.types import TypeDecorator
from sqlalchemy.dialects.mysql.base import MSBinary
from sqlalchemy.schema import Column
import uuid




from flask import (Flask as BaseFlask, Config as BaseConfig)


def register_blueprints(app, package_name, package_path):
    """Register all Blueprint instances on the specified Flask application found
    in all modules for the specified package.

    :param app: the Flask application
    :param package_name: the package name
    :param package_path: the package path
    """
    rv = []
    for _, name, _ in pkgutil.iter_modules(package_path):
        m = importlib.import_module('%s.%s' % (package_name, name))
        for item in dir(m):
            item = getattr(m, item)
            if isinstance(item, Blueprint):
                app.register_blueprint(item)
            rv.append(item)
    return rv


class JSONEncoder(BaseJSONEncoder):
    """Custom :class:`JSONEncoder` which respects objects that include the
    :class:`JsonSerializer` mixin.
    """
    def default(self, obj):
        if isinstance(obj, JsonSerializer):
            return obj.to_json()
        return super(JSONEncoder, self).default(obj)


class JsonSerializer(object):
    """A mixin that can be used to mark a SQLAlchemy model class which
    implements a :func:`to_json` method. The :func:`to_json` method is used
    in conjuction with the custom :class:`JSONEncoder` class. By default this
    mixin will assume all properties of the SQLAlchemy model are to be visible
    in the JSON output. Extend this class to customize which properties are
    public, hidden or modified before being being passed to the JSON serializer.
    """

    __json_public__ = None
    __json_hidden__ = None
    __json_modifiers__ = None

    def get_field_names(self):
        for p in self.__mapper__.iterate_properties:
            yield p.key

    def to_json(self):
        field_names = self.get_field_names()

        public = self.__json_public__ or field_names
        hidden = self.__json_hidden__ or []
        modifiers = self.__json_modifiers__ or dict()

        rv = dict()
        for key in public:
            rv[key] = getattr(self, key)
        for key, modifier in modifiers.items():
            value = getattr(self, key)
            rv[key] = modifier(value, self)
        for key in hidden:
            rv.pop(key, None)
        return rv

class UUID(TypeDecorator):
    impl = MSBinary

    def __init__(self):
        self.impl.length = 16
        TypeDecorator.__init__(self, length=self.impl.length)

    def process_bind_param(self, value, dialect=None):
        if value and isinstance(value, uuid.UUID):
            return value.bytes
        elif value and not isinstance(value, uuid.UUID):
            raise ValueError, 'value %s is not a valid uuid.UUID' % value
        else:
            return None

    def process_result_value(self, value, dialect=None):
        if value:
            return uuid.UUID(bytes=value)
        else:
            return None

    def is_mutable(self):
        return False


id_column_name = "id"


def id_column():
    import uuid

    return Column(id_column_name, UUID(), primary_key=True, default=uuid.uuid4)


class Config(BaseConfig):
    def from_heroku(self):
        # Register database schemes in URLs.
        for key in ['DATABASE_URL']:
            if key in os.environ:
                self['SQLALCHEMY_DATABASE_URI'] = os.environ[key]
                break

        if "MONGOHQ_URL" in os.environ:
            self['MONGODB_HOST'] = os.environ["MONGOHQ_URL"]
            uri = urlparse(os.environ["MONGOHQ_URL"])
            self['MONGODB_DATABASE'] = uri.path[1:]

        if "REDISTOGO_URL" in os.environ:
            self['REDIS_HOST'] = os.environ["REDISTOGO_URL"]
            self['BROKER_URL'] = os.environ["REDISTOGO_URL"]

        if "ITCHY_VANITY_SUB" in os.environ:
            self["VANITY_SUB"] = os.environ["ITCHY_VANITY_SUB"]

        for key in ['SECRET_KEY', 'GOOGLE_ANALYTICS_ID', 'ADMIN_CREDENTIALS']:
            if key in os.environ:
                self[key] = os.environ[key]

        for key_prefix in ['TWITTER', 'FACEBOOK']:
            for key_suffix in ['key', 'secret']:
                ev = '%s_CONSUMER_%s' % (key_prefix, key_suffix.upper())
                if ev in os.environ:
                    social_key = 'SOCIAL_' + key_prefix
                    oauth_key = 'consumer_' + key_suffix
                    self[social_key]['oauth'][oauth_key] = os.environ[ev]

    def from_yaml(self, root_path):
        print root_path
        env = os.environ.get('FLASK_ENV', 'development').upper()
        self['ENVIRONMENT'] = env.lower()
        for fn in ('app', 'credentials'):
            config_file = os.path.abspath(os.path.join(os.path.dirname(root_path), '../configs', '%s.yml' % fn))
            try:
                with open(config_file) as f:
                    c = yaml.load(f)

                c = c.get(env, c)

                for key in c.iterkeys():
                    if key.isupper():
                        self[key] = c[key]
            except:
                pass


class Flask(BaseFlask):
    """Extended version of `Flask` that implements custom config class
    and adds `register_middleware` method"""

    def make_config(self, instance_relative=False):
        root_path = self.root_path
        if instance_relative:
            root_path = self.instance_path
        return Config(root_path, self.default_config)

