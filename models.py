from flask import Flask
from flask_admin.contrib.sqla.fields import QuerySelectField
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
    id_department = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name_department = db.Column(db.String(235))
    address_department = db.Column(db.String(235))
    buildings = db.relationship('Building', backref='department', lazy=True)

class Building(db.Model):
    __tablename__ = 'buildings'
    id_building = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name_building = db.Column(db.String(235))
    id_department = db.Column(db.Integer, db.ForeignKey('departments.id_department'), nullable=False)
    floors = db.relationship('Floor', backref='building', lazy=True)

class Condition(db.Model):
    __tablename__ = 'conditions'
    id_condition = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name_condition = db.Column(db.String(235))
    mtos = db.relationship('MTO', backref='condition', lazy=True)

class Floor(db.Model):
    __tablename__ = 'floor'
    id_floor = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name_floor = db.Column(db.String(235))
    id_building = db.Column(db.Integer, db.ForeignKey('buildings.id_building'), nullable=False)
    rooms = db.relationship('Room', backref='floor', lazy=True)

class MTO(db.Model):
    __tablename__ = 'mto'
    id_mto = db.Column(db.Integer, primary_key=True, autoincrement=True)
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
    id_room = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name_room = db.Column(db.String(235))
    number_room = db.Column(db.Integer)
    id_floor = db.Column(db.Integer, db.ForeignKey('floor.id_floor'), nullable=False)
    mtos = db.relationship('MTO', backref='room', lazy=True)

class Category(db.Model):
    __tablename__ = 'categories'
    id_category = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name_category = db.Column(db.String(235))
    mtos = db.relationship('MTO', backref='category', lazy=True)

class User(db.Model):
    __tablename__ = 'users'
    id_user = db.Column(db.Integer, primary_key=True, autoincrement=True)
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
    form_columns = ['name_department', 'address_department']
    form_args = {
        'name_department': {'label': 'Название подразделения'},
        'address_department': {'label': 'Адрес подразделения'}
    }

class BuildingAdmin(AdminModelView):
    can_delete = True
    column_display_pk = True
    column_hide_backrefs = False
    column_labels = {
        'id_building': 'ID корпуса',
        'name_building': 'Название корпуса',
        'id_department': 'Подразделение',
        'department.name_department': 'Название подразделения',
    }
    column_list = ('id_building', 'name_building', 'department.name_department')
    form_columns = ['name_building', 'id_department']
    form_extra_fields = {
        'id_department': QuerySelectField(
            label='Подразделение',
            query_factory=lambda: Department.query.all(),
            get_label='name_department',
            allow_blank=False,
            get_pk=lambda item: item.id_department
        )
    }

    def on_model_change(self, form, model, is_created):
        model.id_department = form.id_department.data.id_department if form.id_department.data else None
        super().on_model_change(form, model, is_created)

class FloorAdmin(AdminModelView):
    can_delete = True
    column_display_pk = True
    column_hide_backrefs = False
    column_labels = {
        'id_floor': 'ID этажа',
        'name_floor': 'Название этажа',
        'id_building': 'Корпус',
        'building_name': 'Подразделение - Корпус',
    }
    column_list = ('id_floor', 'name_floor', 'building_name')
    form_columns = ['name_floor', 'id_building']
    form_extra_fields = {
        'id_building': QuerySelectField(
            label='Корпус',
            query_factory=lambda: Building.query.all(),
            get_label=lambda b: f'{b.department.name_department} - {b.name_building}',
            allow_blank=False,
            get_pk=lambda b: b.id_building
        )
    }

    def on_model_change(self, form, model, is_created):
        model.id_building = form.id_building.data.id_building if form.id_building.data else None
        super().on_model_change(form, model, is_created)

    def _building_name_formatter(view, context, model, name):
        return f"{model.building.department.name_department} - {model.building.name_building}"

    column_formatters = {
        'building_name': _building_name_formatter
    }

class RoomAdmin(AdminModelView):
    can_delete = True
    column_display_pk = True
    column_hide_backrefs = False
    column_labels = {
        'id_room': 'ID помещения',
        'name_room': 'Название помещения',
        'number_room': 'Номер помещения',
        'id_floor': 'Этаж',
        'floor_name': 'Подразделение - Корпус - Этаж',
    }
    column_list = ('id_room', 'name_room', 'number_room', 'floor_name')
    form_columns = ['name_room', 'number_room', 'id_floor']
    form_extra_fields = {
        'id_floor': QuerySelectField(
            label='Этаж',
            query_factory=lambda: Floor.query.all(),
            get_label=lambda r: f'{r.building.department.name_department} - {r.building.name_building} - {r.name_floor}',
            allow_blank=False,
            get_pk=lambda r: r.id_floor
        )
    }

    def on_model_change(self, form, model, is_created):
        model.id_floor = form.id_floor.data.id_floor if form.id_floor.data else None
        super().on_model_change(form, model, is_created)

    def _floor_name_formatter(view, context, model, name):
        return f"{model.floor.building.department.name_department} - {model.floor.building.name_building} - {model.floor.name_floor}"

    column_formatters = {
        'floor_name': _floor_name_formatter
    }

class ConditionAdmin(AdminModelView):
    can_delete = True
    column_display_pk = True
    column_hide_backrefs = False
    column_labels = {
        'id_condition': 'ID состояния',
        'name_condition': 'Название состояния'
    }
    form_columns = ['name_condition']
    form_args = {
        'name_condition': {'label': 'Название состояния'}
    }

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
    form_columns = ['name_mto', 'inventory_number', 'date_setup', 'date_last_repair', 'id_condition', 'id_category', 'id_room', 'date_made', 'presense']
    form_extra_fields = {
        'id_condition': QuerySelectField('Состояние', query_factory=lambda: Condition.query.all(), get_label='name_condition', allow_blank=True),
        'id_category': QuerySelectField('Категория', query_factory=lambda: Category.query.all(), get_label='name_category', allow_blank=True),
        'id_room': QuerySelectField('Помещение', query_factory=lambda: Room.query.all(), get_label='name_room', allow_blank=True)
    }

class CategoryAdmin(AdminModelView):
    can_delete = True
    column_display_pk = True
    column_hide_backrefs = False
    column_labels = {
        'id_category': 'ID категории',
        'name_category': 'Название категории'
    }
    form_columns = ['name_category']
    form_args = {
        'name_category': {'label': 'Название категории'}
    }

class UserAdmin(AdminModelView):
    can_delete = True
    column_display_pk = True
    column_hide_backrefs = False
    column_labels = {
        'id_user': 'ID пользователя',
        'fio_user': 'ФИО пользователя',
        'flag_admin': 'Администратор',
        'login': 'Логин',
        'password': 'Пароль'
    }
    form_columns = ['fio_user', 'flag_admin', 'login', 'password']
    form_args = {
        'fio_user': {'label': 'ФИО пользователя'},
        'flag_admin': {'label': 'Администратор'},
        'login': {'label': 'Логин'},
        'password': {'label': 'Пароль'}
    }

    def on_model_change(self, form, model, is_created):
        # Хешируем пароль, если он задан в форме
        if form.password.data:
            model.password = generate_password_hash(form.password.data)

        super().on_model_change(form, model, is_created)


# Создание админки
admin = Admin(app, name='Административная панель', template_mode='bootstrap4')
admin.add_view(DepartmentAdmin(Department, db.session, name='Подразделения'))
admin.add_view(BuildingAdmin(Building, db.session, name='Корпуса'))
admin.add_view(FloorAdmin(Floor, db.session, name='Этажи'))
admin.add_view(RoomAdmin(Room, db.session, name='Помещения'))
admin.add_view(ConditionAdmin(Condition, db.session, name='Состояния'))
admin.add_view(CategoryAdmin(Category, db.session, name='Категории'))
# admin.add_view(MTOAdmin(MTO, db.session, name='МТО'))
admin.add_view(UserAdmin(User, db.session, name='Пользователи'))

if __name__ == '__main__':
    if not os.path.isfile(Config.SQLALCHEMY_DATABASE_URI):
        with app.app_context():
            db.create_all()
            insert_categories()
