from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask import render_template, redirect, url_for, flash, request
from flask_babel import Babel
from flask_babel import lazy_gettext as _

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)


# Настройка Flask-Babel
app.config['BABEL_DEFAULT_LOCALE'] = 'ru'
babel = Babel(app)


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
    id_category = db.Column(db.Integer, db.ForeignKey('categories.id_category'), nullable=False)
    id_room = db.Column(db.Integer, db.ForeignKey('rooms.id_room'), nullable=False)
    date_made = db.Column(db.Date)
    presense = db.Column(db.Integer, default=1)

class Room(db.Model):
    __tablename__ = 'rooms'
    id_room = db.Column(db.Integer, primary_key=True)
    name_room = db.Column(db.String(235))
    number_room = db.Column(db.Integer)
    id_floor = db.Column(db.Integer, db.ForeignKey('floor.id_floor'), nullable=False)
    mtos = db.relationship('MTO', backref='room', lazy=True)

class Category(db.Model):
    __tablename__ = 'categories'
    id_category = db.Column(db.Integer, primary_key=True)
    name_category = db.Column(db.String(235))
    mtos = db.relationship('MTO', backref='category', lazy=True)

class User(db.Model):
    __tablename__ = 'users'
    id_user = db.Column(db.Integer, primary_key=True)
    fio_user = db.Column(db.String(235), nullable=False)
    flag_admin = db.Column(db.Integer, default=0)
    login = db.Column(db.String(235), nullable=False)
    password = db.Column(db.String(235), nullable=False)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id_user)


def insert_categories():
    categories = [
        "Сетевое оборудование",
        "ПК и ноутбуки",
        "Оборудование для лекций и семинаров",
        "Научное и лабораторное оборудование",
        "Офисная техника",
        "Мебель",
        "Уборочная техника",
        "Электротехническое оборудование",
        "Средства обеспечения безопасности",
    ]

    for category_name in categories:
        category = Category(name_category=category_name)
        db.session.add(category)
    db.session.commit()


########################################################################################################################
########################################################################################################################
########################################################################################################################
class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.flag_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))


class DepartmentAdmin(AdminModelView):
    can_delete = True
    column_display_pk = True
    column_hide_backrefs = False
    column_labels = {
        'id_department': 'ID подразделения',
        'name_department': 'Название подразделения',
        'address_department': 'Адрес подразделения'
    }
    column_list = ('id_department', 'name_department', 'address_department')

    def __init__(self, *args, **kwargs):
        super(DepartmentAdmin, self).__init__(*args, **kwargs)
        self.name = 'Подразделения'


class BuildingAdmin(AdminModelView):
    can_delete = True
    column_display_pk = True
    column_hide_backrefs = False
    column_labels = {
        'id_building': 'ID корпуса',
        'name_building': 'Название корпуса',
        'id_department': 'Подразделение'
    }
    column_list = ('id_building', 'name_building', 'department.name_department')

    def __init__(self, *args, **kwargs):
        super(BuildingAdmin, self).__init__(*args, **kwargs)
        self.name = 'Корпуса'


class ConditionAdmin(AdminModelView):
    can_delete = True
    column_display_pk = True
    column_hide_backrefs = False
    column_labels = {
        'id_condition': 'ID состояния',
        'name_condition': 'Название состояния'
    }
    column_list = ('id_condition', 'name_condition')

    def __init__(self, *args, **kwargs):
        super(ConditionAdmin, self).__init__(*args, **kwargs)
        self.name = 'Состояния'


class FloorAdmin(AdminModelView):
    can_delete = True
    column_display_pk = True
    column_hide_backrefs = False
    column_labels = {
        'id_floor': 'ID этажа',
        'name_floor': 'Название этажа',
        'id_building': 'Корпус'
    }
    column_list = ('id_floor', 'name_floor', 'building.name_building')

    def __init__(self, *args, **kwargs):
        super(FloorAdmin, self).__init__(*args, **kwargs)
        self.name = 'Этажи'


class MTOAdmin(AdminModelView):
    can_delete = True
    column_display_pk = True
    column_hide_backrefs = False
    column_labels = {
        'id_mto': 'ID МТО',
        'name_mto': 'Название МТО',
        'inventory_number': 'Инвентарный Номер',
        'date_setup': 'Дата Установки',
        'date_last_repair': 'Дата Последнего Ремонта',
        'id_condition': 'Состояние',
        'id_category': 'Категория',
        'id_room': 'Помещение',
        'date_made': 'Дата Изготовления',
        'presense': 'Наличие'
    }
    column_list = ('id_mto', 'name_mto', 'inventory_number', 'date_setup', 'date_last_repair',
                   'condition.name_condition', 'category.name_category', 'room.name_room', 'date_made', 'presense')

    def __init__(self, *args, **kwargs):
        super(MTOAdmin, self).__init__(*args, **kwargs)
        self.name = 'МТО'


class RoomAdmin(AdminModelView):
    can_delete = True
    column_display_pk = True
    column_hide_backrefs = False
    column_labels = {
        'id_room': 'ID помещения',
        'name_room': 'Название помещения',
        'number_room': 'Номер помещения',
        'id_floor': 'Этаж'
    }
    column_list = ('id_room', 'name_room', 'number_room', 'floor.name_floor')

    def __init__(self, *args, **kwargs):
        super(RoomAdmin, self).__init__(*args, **kwargs)
        self.name = 'Помещения'


class CategoryAdmin(AdminModelView):
    can_delete = True
    column_display_pk = True
    column_hide_backrefs = False
    column_labels = {
        'id_category': 'ID категории',
        'name_category': 'Название категории'
    }
    column_list = ('id_category', 'name_category')

    def __init__(self, *args, **kwargs):
        super(CategoryAdmin, self).__init__(*args, **kwargs)
        self.name = 'Категории'


class UserAdmin(AdminModelView):
    can_delete = True
    column_display_pk = True
    column_hide_backrefs = False
    column_labels = {
        'id_user': 'ID Пользователя',
        'fio_user': 'ФИО Пользователя',
        'flag_admin': 'Администратор',
        'login': 'Логин',
        'password': 'Пароль'
    }
    column_list = ('id_user', 'fio_user', 'flag_admin', 'login', 'password')

    def __init__(self, *args, **kwargs):
        super(UserAdmin, self).__init__(*args, **kwargs)
        self.name = 'Пользователи'


admin = Admin(app, name='Административная Панель', template_mode='bootstrap3')
admin.add_view(DepartmentAdmin(Department, db.session))
admin.add_view(BuildingAdmin(Building, db.session))
admin.add_view(FloorAdmin(Floor, db.session))
admin.add_view(RoomAdmin(Room, db.session))
admin.add_view(ConditionAdmin(Condition, db.session))
admin.add_view(CategoryAdmin(Category, db.session))
admin.add_view(MTOAdmin(MTO, db.session))
admin.add_view(UserAdmin(User, db.session))


if __name__ == '__main__':
    if not os.path.isfile(Config.SQLALCHEMY_DATABASE_URI):
        with app.app_context():
            db.create_all()
            insert_categories()
