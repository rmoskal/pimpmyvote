# -*- coding: utf-8 -*-
"""
    overholt.manage.users
    ~~~~~~~~~~~~~~~~~~~~~

    user management commands
"""

from flask.ext.script import Command, prompt, prompt_pass
from flask_security.forms import RegisterForm
from flask_security.registerable import register_user
from werkzeug.datastructures import MultiDict
from flask.ext.script import Manager
from pimp.services import users
from pimp.api import create_app
from pimp.core import db

manager = Manager(create_app())

@manager.command
def create_user():
    email = prompt('Email')
    password = prompt_pass('Password')
    password_confirm = prompt_pass('Confirm Password')
    data = MultiDict(dict(email=email, password=password, password_confirm=password_confirm))
    form = RegisterForm(data, csrf_enabled=False)
    if form.validate():
        user = register_user(email=email, password=password)
        print '\nUser created successfully'
        print 'User(id=%s email=%s)' % (user.id, user.email)
        return
    print '\nError creating user:'
    for errors in form.errors.values():
        print '\n'.join(errors)

@manager.command
def delete_user():
    email = prompt('Email')
    user = users.first(email=email)
    if not user:
        print 'Invalid user'
        return
    users.delete(user)
    print 'User deleted successfully'

@manager.command
def list_users():
    for u in users.all():
        print 'User(id=%s email=%s)' % (u.id, u.email)

@manager.command
def db_drop():
    db.drop_all()
    db.create_all()

@manager.command
def db_create():
    db.drop_all()
    db.create_all()


if __name__ == "__main__":
    manager.run()
