from datetime import datetime
from pprint import pprint

from flask import jsonify
from sqlalchemy import asc

from models import *
from forms import *

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'


@app.route('/')
def index():
    return render_template('index.html')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/mto')
@login_required
def mto():
    departments = Department.query.order_by(Department.name_department.asc()).all()
    return render_template('mto.html', departments=departments)


@app.route('/getdata', methods=['POST'])
def getdata():
    if 'id_department' in request.form:
        id_department = request.form['id_department']
        data = Building.query.filter_by(id_department=id_department).order_by(Building.name_building.asc()).all()
        data_list = [dict((col.name, getattr(dir, col.name)) for col in dir.__table__.columns) for dir in data]
    elif 'id_building' in request.form:
        id_building = request.form['id_building']
        data = Floor.query.filter_by(id_building=id_building).order_by(Floor.name_floor.asc()).all()
        data_list = [dict((col.name, getattr(dir, col.name)) for col in dir.__table__.columns) for dir in data]
    elif 'id_floor' in request.form:
        id_floor = request.form['id_floor']
        data = Room.query.filter_by(id_floor=id_floor).order_by(Room.number_room.asc()).all()
        data_list = [dict((col.name, getattr(dir, col.name)) for col in dir.__table__.columns) for dir in data]
    elif 'id_room' in request.form:
        id_room = int(request.form['id_room'])
        if id_room > 0:
            data_list = ['OK']
        else:
            data_list = ['ERR1']
    else:
        data_list = ['ERR2']

    return jsonify(data_list)


@app.route('/filtermto', methods=['POST'])
def filtermto():
    id_room = request.form.get('id_room')
    if id_room:
        categories = Category.query.order_by(Category.name_category.asc()).all()
        categories_list = [dict((col.name, getattr(dir, col.name)) for col in dir.__table__.columns) for dir in categories]

        conditions = Condition.query.order_by(Condition.name_condition.asc()).all()
        conditions_list = [dict((col.name, getattr(dir, col.name)) for col in dir.__table__.columns) for dir in conditions]

        filtered_mto = (db.session.query(MTO, Category.name_category, Condition.name_condition)
                        .join(Condition, MTO.id_condition == Condition.id_condition)
                        .join(Category, MTO.id_category == Category.id_category)
                        .filter(MTO.id_room == id_room)
                        .order_by(asc(Category.name_category), asc(MTO.name_mto))
                        .all())
        mtos = []
        for mto, name_category, name_condition in filtered_mto:
            mto_dict = vars(mto)
            mto_dict['name_category'] = name_category
            mto_dict['name_condition'] = name_condition
            # pprint(mto_dict)
            mtos.append(mto_dict)
        # Передача данных в шаблон
        return render_template('filtered.html', mtos=mtos, categories_list=categories_list, conditions_list=conditions_list)
    else:
        return render_template('filtered.html', mtos=[], categories_list=[], conditions_list=[])


@app.route('/addmto', methods=['POST'])
def addmto():
    id_room = request.form.get('id_room')
    id_category = request.form.get('id_category')
    id_condition = request.form.get('id_condition')
    presense = request.form.get('presense')
    name_mto = request.form.get('name_mto')
    inventory_number = request.form.get('inventory_number')
    date_made = request.form.get('date_made')
    date_setup = request.form.get('date_setup')
    date_last_repair = request.form.get('date_last_repair')

    if id_category and id_condition and presense and name_mto and inventory_number and date_made and date_setup:

        date_setup = datetime.strptime(date_setup, '%Y-%m-%d').date() if date_setup else None
        date_last_repair = datetime.strptime(date_last_repair,'%Y-%m-%d').date() if date_last_repair else None
        date_made = datetime.strptime(date_made, '%Y-%m-%d').date() if date_made else None

        new_mto = MTO(
            name_mto=name_mto,
            inventory_number=inventory_number,
            date_setup=date_setup,
            date_last_repair=date_last_repair,
            id_condition=id_condition,
            id_category=id_category,
            id_room=id_room,
            date_made=date_made,
            presense=presense
        )
        db.session.add(new_mto)
        db.session.commit()
        return ['OK']
    else:
        return ['ERR']


@app.route('/updatemto', methods=['POST'])
def updatemto():
    id_mto = request.form['id_mto']
    mto = MTO.query.get_or_404(id_mto)

    mto.name_mto = request.form['name']
    mto.inventory_number = request.form['inv']
    mto.date_made = datetime.strptime(request.form['made'], '%Y-%m-%d')
    mto.date_setup = datetime.strptime(request.form['setup'], '%Y-%m-%d')
    mto.date_last_repair = datetime.strptime(request.form['repair'], '%Y-%m-%d') if request.form['repair'] else None
    mto.id_condition = request.form['condition']
    mto.id_category = request.form['category']
    mto.presense = request.form['presense']

    db.session.commit()
    return jsonify({'message': 'МТО успешно обновлено'})


@app.route('/delmto', methods=['POST'])
def delmto():
    id_mto = request.form['id_mto']
    mto = MTO.query.get_or_404(id_mto)

    db.session.delete(mto)

    db.session.commit()
    return jsonify({'message': 'МТО успешно удалено'})


@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data).first()
        if user and check_password_hash(user.password, form.password.data):  # пароль хэширован
            login_user(user)
            if user.flag_admin:
                return redirect(url_for('admin.index'))
            else:
                return redirect(url_for('mto'))

    return render_template('login.html', form=form)


@app.route('/auth/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)