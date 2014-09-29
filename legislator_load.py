from petl import *
from pimp.api import create_app
from pimp.core import py_mongo


app = create_app()

'''
Do a fresh import of legislators!
'''

table1 = fromcsv('./source_data/legislators.csv')
data = iterdicts(table1)
with app.app_context():
    ls = py_mongo.db.legislators
    ls.remove()
    for row in data:
        ls.insert(row)
