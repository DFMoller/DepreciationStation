
# Database Models

from . import db
from sqlalchemy.sql import func


# class Car(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     brand = db.Column(db.String(100))
#     model = db.Column(db.String(100))
#     year = db.Column(db.String(100))
#     color = db.Column(db.String(100))
#     values = db.relationship('Value') # notice here it is a Capital letter, not very consistent, but correct

# class Value(db.Model): # db.Model is like a blueprint
#     id = db.Column(db.Integer, primary_key=True)
#     value = db.Column(db.Float)
#     mileage = db.Column(db.Float)
#     date = db.Column(db.String(100))
#     car_id = db.Column(db.Integer, db.ForeignKey('car.id')) # will store id of one of the cars

class Search(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.String(100))
    color = db.Column(db.String(100))
    readings = db.relationship('History')
    todays = db.relationship('Today')

class Today(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    search_id = db.Column(db.Integer, db.ForeignKey('search.id'))
    title = db.Column(db.String(100))
    value = db.Column(db.Float)
    mileage = db.Column(db.Float)
    date = db.Column(db.String(100))
    rel_link = db.Column(db.String(100))

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    search_id = db.Column(db.Integer, db.ForeignKey('search.id'))
    median_value = db.Column(db.Float)
    date = db.Column(db.String(100))