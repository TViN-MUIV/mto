from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os
from insert_data import *

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

class Department(db.Model):
    __tablename__ = 'departments'
    id_department = db.Column(db.Integer, primary_key=True)
    name_department = db.Column(db.String(235))
    address_department = db.Column(db.String(235))
    buildings = db.relationship('Building', backref='department', lazy=True)

class Building(db.Model):
    __tablename__ = 'buildings'
    id_building = db.Column(db.Integer, primary_key=True)
    name_building = db.Column(db.String(235))
    id_department = db.Column(db.Integer, db.ForeignKey('departments.id_department'), nullable=False)
    floors = db.relationship('Floor', backref='building', lazy=True)

class Category(db.Model):
    __tablename__ = 'categories'
    id_category = db.Column(db.Integer, primary_key=True)
    name_category = db.Column(db.String(235))
    subcategories = db.relationship('Subcategory', backref='category', lazy=True)

class Condition(db.Model):
    __tablename__ = 'conditions'
    id_condition = db.Column(db.Integer, primary_key=True)
    name_condition = db.Column(db.String(235))
    mtos = db.relationship('MTO', backref='condition', lazy=True)

class Floor(db.Model):
    __tablename__ = 'floor'
    id_floor = db.Column(db.Integer, primary_key=True)
    name_floor = db.Column(db.String(235))
    id_building = db.Column(db.Integer, db.ForeignKey('buildings.id_building'), nullable=False)
    rooms = db.relationship('Room', backref='floor', lazy=True)

class MTO(db.Model):
    __tablename__ = 'mto'
    id_mto = db.Column(db.Integer, primary_key=True)
    name_mto = db.Column(db.String(235))
    inventory_number = db.Column(db.String(235))
    date_setup = db.Column(db.Date)
    date_last_repair = db.Column(db.Date)
    id_condition = db.Column(db.Integer, db.ForeignKey('conditions.id_condition'), nullable=False)
    id_subcategory = db.Column(db.Integer, db.ForeignKey('subcategories.id_subcategory'), nullable=False)
    id_room = db.Column(db.Integer, db.ForeignKey('rooms.id_room'), nullable=False)
    date_made = db.Column(db.Date)

class Room(db.Model):
    __tablename__ = 'rooms'
    id_room = db.Column(db.Integer, primary_key=True)
    name_room = db.Column(db.String(235))
    number_room = db.Column(db.Integer)
    id_floor = db.Column(db.Integer, db.ForeignKey('floor.id_floor'), nullable=False)
    mtos = db.relationship('MTO', backref='room', lazy=True)

class Subcategory(db.Model):
    __tablename__ = 'subcategories'
    id_subcategory = db.Column(db.Integer, primary_key=True)
    name_subcategory = db.Column(db.String(235))
    id_category = db.Column(db.Integer, db.ForeignKey('categories.id_category'), nullable=False)
    mtos = db.relationship('MTO', backref='subcategory', lazy=True)

class User(db.Model):
    __tablename__ = 'users'
    id_user = db.Column(db.Integer, primary_key=True)
    fio_user = db.Column(db.String(235))
    flag_admin = db.Column(db.Integer, default=0)

if __name__ == '__main__':
    if not os.path.isfile(Config.SQLALCHEMY_DATABASE_URI):
        with app.app_context():
            db.create_all()
            insert_categories()
