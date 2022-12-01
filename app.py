from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123054@localhost/pc_assembling'
db = SQLAlchemy(app)


class Users(db.Model):
    id_U = db.Column(db.Integer, primary_key=True)
    surname = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    patronymic = db.Column(db.String(50), nullable=True)
    birthday = db.Column(db.Date, nullable=False)
    passport = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    passw = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return '<Users %r>' % self.id_U


class Orders(db.Model):
    id_O = db.Column(db.Integer, primary_key=True)
    cost = db.Column(db.Integer, nullable=True)
    state = db.Column(db.String(200), nullable=False)

    Users_id_U = db.Column(db.Integer, db.ForeignKey('users.id_U'), nullable=False)

    def __repr__(self):
        return '<Orders %r>' % self.id_O


class Component_Types(db.Model):
    id_CT = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<Component_Types %r>' % self.id_CT


class Components(db.Model):
    id_C = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Integer, nullable=False)

    Orders_id_O = db.Column(db.Integer, db.ForeignKey('orders.id_O'), nullable=False)
    Component_Types_id_CT = db.Column(db.Integer, db.ForeignKey('component_types.id_CT'), nullable=False)

    def __repr__(self):
        return '<Components %r>' % self.id_C


class Professions(db.Model):
    id_P = db.Column(db.Integer, primary_key=True)
    profession = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<Professions %r>' % self.id_P


class Duties(db.Model):
    id_D = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    Description = db.Column(db.Text, nullable=False)

    Professions_id_P = db.Column(db.Integer, db.ForeignKey('professions.id_P'), nullable=False)

    def __repr__(self):
        return '<Duties %r>' % self.id_D


class Masters(db.Model):
    id_M = db.Column(db.Integer, primary_key=True)
    surname = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    patronymic = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), nullable=False)
    passw = db.Column(db.String(100), nullable=True)

    Professions_id_P = db.Column(db.Integer, db.ForeignKey('professions.id_P'), nullable=False)
    Orders_id_O = db.Column(db.Integer, db.ForeignKey('orders.id_O'), nullable=False)

    def __repr__(self):
        return '<Masters %r>' % self.id_M


class log_tab(db.Model):
    id_L = db.Column(db.Integer, primary_key=True)
    log_time = db.Column(db.Date, nullable=False)
    N_state = db.Column(db.String(200), nullable=False)
    O_state = db.Column(db.String(200), nullable=False)


db.create_all()


@app.route('/')
@app.route('/home')
def index():
    return render_template("index.html")


@app.route('/auth', methods=['POST', 'GET'])
def auth():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        User = Users.query.filter_by(email=login).first();
        Master = Masters.query.filter_by(email=login).first();

        if (User is not None) and (login == User.email):
            if password == User.passw:
                return redirect('/orders', name=User.name)
            else:
                return "Неверный пароль!"
        elif (Master is not None) and (login == Master.email):
            if password == Master.passw:
                return redirect('/add-order', name=Master.name)
            else:
                return "Неверный пароль!"
        else:
            return login + " - Неверный логин! Вы можете зарегистрироваться, написав" \
                           "на нашу корпоративную почту: admin@pc-assembler.ru"

    else:
        return render_template("authorisation.html")


# return login + " - Неверный логин! Вы можете зарегистрироваться, написав " \
#                          "на нашу корпоративную почту: admin@pc-assembler.ru"
#      try:
#           for master in Masters:
#               if user.login == Masters.email:
#                   Master = Masters.query.filter_by(Masters.email=user.login).first()
#                      return redirect('/orders')
#          for users in Users:
#              if user.login == Users.email:
#                  if user.password == Users.passw:
#                      User = Users.query.get(user.login)
#     except:
#         return "Oops"
# else:
#    return render_template("authorisation.html")


@app.route('/orders')
def orders():
    # пример сортировки: orders = Orders.query.order_by(Orders.поле).all()

    orders = Orders.query.all()
    return render_template("orders.html", orders=orders)


@app.route('/orders/<int:id_O><int:Users_id_U>')
def orders_detail(id_O, Users_id_U):
    order = Orders.query.get(id_O)
    User = Users.query.get(Users_id_U)
    Master = Masters.query.filter_by(Orders_id_O=order.id_O).first()
    return render_template("orders-detail.html", order=order, User=User, Master=Master)


@app.route('/orders/<int:id_O>/delete')
def orders_delete(id_O):
    order = Orders.query.get_or_404(id_O)
    try:
        db.session.delete(order)
        db.session.commit()
        return redirect("/orders")
    except:
        return "При удалении статьи произошла ошибка :("


@app.route('/orders/<int:id_O>/update', methods=['POST', 'GET'])
def order_update(id_O):
    order = Orders.query.get(id_O)
    if request.method == 'POST':
        order.state = request.form['state']
        order.cost = request.form['cost']
        try:
            db.session.commit()
            return redirect('/orders')
        except:
            return "При обновлении статуса заказа произошла ошибка :("
    else:
        return render_template("order_update.html", order=order)


@app.route('/add-order', methods=['POST', 'GET'])
def add_order():
    if request.method == 'POST':
        state = request.form['state']
        Users_id_U = request.form['Users_id_U']
        cost = request.form['cost']
        ord = Orders(state=state, Users_id_U=Users_id_U, cost=cost)

        try:
            db.session.add(ord)
            db.session.commit()
            return redirect('/orders')
        except:
            return "При добавлении заказа произошла ошибка :("
    else:
        return render_template("add_order.html")


@app.route('/user/<string:name>/<int:id>')
def user(name, id):
    return 'Page of User: ' + name + " with id:" + str(id)


if __name__ == "__main__":
    app.run(debug=True)

''' все ошибки выводятся на сайте, для конечного сайта указать debug = False'''
