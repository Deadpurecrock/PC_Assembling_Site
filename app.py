from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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


class Messages(db.Model):
    id_Msg = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    time = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Messages %r>' % self.id_Msg

db.create_all()


@app.route('/', methods=['POST', 'GET'])
@app.route('/auth', methods=['POST', 'GET'])
def auth():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        User = Users.query.filter_by(email=login).first();
        Master = Masters.query.filter_by(email=login).first();

        if (User is not None) and (login == User.email):
            if password == User.passw:
                return redirect(url_for('chat', User=User))
            else:
                return "Неверный пароль!"
        elif (Master is not None) and (login == Master.email):
            if password == Master.passw:
                return redirect(url_for('add_order', Master=Master))
            else:
                return "Неверный пароль!"
        else:
            return login + " - Неверный логин! Вы можете зарегистрироваться, написав" \
                           "на нашу корпоративную почту: admin@pc-assembler.ru"

    else:
        return render_template("authorisation.html")


@app.route('/orders')
def orders():
    Master = request.args['Master']
    Master1 = Master[9] + Master[10]
    Master2 = Masters.query.filter_by(id_M=Master1).first()
    orders = Orders.query.all()
    return render_template("orders.html", orders=orders, Master=Master2)

@app.route('/user-order')
def user_order():
    User = request.args['User']
    User1 = User[7] + User[8]
    User2 = Users.query.filter_by(id_U=User1).first()
    orders = Orders.query.filter_by(Users_id_U=User1).all()
    return render_template("user_order.html", orders=orders, User=User2)


@app.route('/orders/<int:id_O><int:Users_id_U>')
def orders_detail(id_O, Users_id_U):
    order = Orders.query.get(id_O)
    User = Users.query.get(Users_id_U)
    Master3 = Masters.query.filter_by(Orders_id_O=order.id_O).first()
    return render_template("orders-detail.html", order=order, User=User, Master=Master3)


@app.route('/orders/<int:id_O>/delete')
def orders_delete(id_O):
    order = Orders.query.get_or_404(id_O)
    try:
        db.session.delete(order)
        db.session.commit()
        return redirect("/orders")
    except:
        return "При удалении статьи произошла ошибка :("


@app.route('/orders/update/<int:id_O><int:id_Mast>', methods=['POST', 'GET'])
def order_update(id_O, id_Mast):
    Master = Masters.query.filter_by(id_M=id_Mast).first()
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
        return render_template("order_update.html", order=order, Master=Master)


@app.route('/add-order/', methods=['POST', 'GET'])
def add_order():
    Master = request.args['Master']
    Master1 = Master[9] + Master[10]
    Master2 = Masters.query.filter_by(id_M=Master1).first()
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
        return render_template("add_order.html", Master=Master2)


@app.route('/chat', methods=['POST', 'GET'])
def chat():
    User = request.args['User']
    User1 = User[7] + User[8]
    User2 = Users.query.filter_by(id_U=User1).first()
    messages = Messages.query.order_by(Messages.time).all()
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        message = request.form['message']
        msg = Messages(username=username, email=email, message=message)
        try:
            db.session.add(msg)
            db.session.commit()
            return redirect(url_for('chat', User=User))
        except:
            return "При отправке сообщения произошла ошибка :("
    else:
        return render_template("chat_user.html", User=User2, messages=messages)

@app.route('/chat-master', methods=['POST', 'GET'])
def chat_master():
    Master = request.args['Master']
    Master1 = Master[9] + Master[10]
    Master2 = Masters.query.filter_by(id_M=Master1).first()
    messages = Messages.query.order_by(Messages.id_Msg).all()
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        message = request.form['message']
        msg = Messages(username=username, email=email, message=message)
        try:
            db.session.add(msg)
            db.session.commit()
            return redirect(url_for('chat_master', Master=Master2))
        except:
            return "При отправке сообщения произошла ошибка :("
    else:
        return render_template("chat_master.html", Master=Master2, messages=messages)

@app.route('/chat-master/<int:id_Msg>/<int:id_Mast>/delete')
def messages_delete(id_Msg, id_Mast):
    Master = Masters.query.filter_by(id_M=id_Mast).first()
    msg = Messages.query.get_or_404(id_Msg)
    try:
        db.session.delete(msg)
        db.session.commit()
        return redirect(url_for('chat_master', Master=Master))
    except:
        return "При удалении сообщения произошла ошибка :("

if __name__ == "__main__":
    app.run(debug=True)

''' все ошибки выводятся на сайте, для конечного сайта указать debug = False'''
