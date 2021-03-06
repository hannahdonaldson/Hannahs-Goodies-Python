from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy 
from flask_cors import CORS 
from flask_heroku import Heroku 
import stripe
import config
from flask_bcrypt import Bcrypt

stripe_keys = {
    'secret_key': config.SECRET_KEY,
    'publishable_key': config.PUBLISHABLE_KEY 
}

stripe.api_key = stripe_keys['secret_key']

app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgres://bxsswwybqhvhic:b2fddf8a534912f868473b8fe9e66f66e153dbb02febfe1cb8b7041bfa11cb70@ec2-23-23-241-119.compute-1.amazonaws.com:5432/d4ibc8jtbqqp86'

heroku = Heroku(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    __tablename__ ="user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(), nullable=False)
    user_type = db.Column(db.String(40), nullable=False)
    cart = db.relationship('Cart', backref='user', lazy=True)
    orders = db.relationship('Order', backref='user', lazy=True)

    def __init__(self, name, email, password, user_type):
        self.name = name
        self.email = email
        self.password = password
        self.user_type = user_type


class Cart(db.Model):
    __tablename__ = "cart"
    id = db.Column(db.Integer, primary_key=True)
    qty = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)

   

    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    cart_items = db.relationship('Cart_item', backref='cart', lazy = True)


    def __init__(self, qty, total, user_id):
        self.qty = qty
        self.total = total
        self.user_id = user_id


class Goodies(db.Model):
    __tablename__ ="goodies"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    summary = db.Column(db.String(1000), nullable=False)
    cost = db.Column(db.Float, nullable=False)
    goodieType = db.Column(db.String(40), nullable=False)
    goodie_url = db.Column(db.String(1000))
    cart_items = db.relationship('Cart_item', backref='goodies', lazy=True)
    order_items = db.relationship('Order_item', backref='goodies', lazy=True)
    

    def __init__(self, title, summary, cost, goodieType, goodie_url):
        self.title = title
        self.summary = summary
        self.cost = cost
        self.goodieType = goodieType
        self.goodie_url = goodie_url
    #     # This is string interpalation in python
    #     # the % self.title is setting a value to %r


class Cart_item(db.Model):
    __tablename__="cart_item"
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey(Cart.id))
    goodie_id = db.Column(db.Integer, db.ForeignKey(Goodies.id))
    
    def __init__(self, cart_id, goodie_id):
      self.cart_id = cart_id
      self.goodie_id = goodie_id

# Order
class Order(db.Model):
    __tablename__ ="order"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    date = db.Column(db.String(120), nullable=False)
    total = db.Column(db.Float, nullable=False)
    order_items = db.relationship('Order_item', backref='order', lazy=True)
    

    def __init__(self, user_id, date, total):
        self.user_id = user_id
        self.date = date
        self.total = total


class Order_item(db.Model):
    __tablename__ ="order_item"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    goodie_id = db.Column(db.Integer, db.ForeignKey('goodies.id'), nullable=False)
    

    def __init__(self, order_id, goodie_id):
        self.order_id = order_id
        self.goodie_id = goodie_id

# class Address(db.Model):
#     __tablename__ ="order_item"
#     id = db.Column(db.Integer, primary_key=True)
#     order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
#     goodie_id = db.Column(db.Integer, db.ForeignKey('goodies.id'), nullable=False)
    

#     def __init__(self, order_id, goodie_id):
#         self.order_id = order_id
#         self.goodie_id = goodie_id



# Routes go here

@app.route("/")
def home():
    return "<h1>Hello World</h1>"


@app.route('/goodies', methods=['GET'])
def return_goodies():
    all_goodies = db.session.query(Goodies.id, Goodies.title, Goodies.summary, Goodies.cost, Goodies.goodieType, Goodies.goodie_url).all()
    return jsonify(all_goodies)

@app.route('/goodie/<id>', methods = ['GET'])
def return_single_goodie(id):
    one_goodie = db.session.query(Goodies.id, Goodies.title, Goodies.summary, Goodies.cost, Goodies.goodieType, Goodies.goodie_url).filter(Goodies.id == id).first()
    return jsonify(one_goodie)

@app.route('/goodie/input', methods=['POST'])
def input_goodie():
    if request.content_type == 'application/json':
        post_data = request.get_json()
        title = post_data.get('title')
        summary = post_data.get('summary')
        cost = post_data.get('cost')
        goodieType = post_data.get('goodieType')
        goodie_url = post_data.get('goodie_url')

        record = Goodies(title, summary, cost, goodieType, goodie_url)
        db.session.add(record)
        db.session.commit()
        return jsonify("Data Posted")
    return jsonify("Error adding Goodie")

@app.route('/update_goodie/<id>', methods=['PUT'])
def goodie_update(id):
    if request.content_type == 'application/json':
        put_data = request.get_json()
        
        title = post_data.get('title')
        summary = post_data.get('summary')
        cost = post_data.get('cost')
        goodieType = post_data.get('goodieType')
        goodie_url = post_data.get('goodie_url')

        record = db.session.query(Goodie).get(id)
        record.title = title
        record.summary = summary
        record.cost = cost
        record.goodieType = goodieType
        record.goodie_url = goodie_url
        db.session.commit()
        return jsonify("Compleded Update")
    return jsonify("Update Failed")

@app.route('/goodie/delete/<id>', methods=["DELETE"])
def delete_goodie(id):
    goodie = db.session.query(Goodie).get(id)
    db.session.delete(goodie)
    db.session.commit()
    return jsonify("Completed Delete action")

@app.route('/goodie/<goodieType>', methods = ['GET'])
def return_goodie_catagory(goodieType):
    goodie_catagory = db.session.query(Goodies.id, Goodies.title, Goodies.summary, Goodies.cost, Goodies.goodieType, Goodies.goodie_url).filter(Goodies.id == id).first()
    return jsonify(goodie_catagory)

@app.route('/register', methods=['POST'])
def register():
    if request.content_type == 'application/json':
        post_data = request.get_json()

        name = post_data.get('name')
        email = post_data.get('email')
        password = post_data.get('password')
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user_type = post_data.get('user_type')

        reg = User(name, email, hashed_password, user_type)
        db.session.add(reg)
        db.session.commit()
        return jsonify("Data Posted")
    return jsonify('Something went wrong')


@app.route('/login', methods=['POST'])
def login():
    if request.content_type == 'application/json':
        post_data = request.get_json()
        check_email = db.session.query(User.email).filter(User.email == post_data.get("email")).first()
        if check_email is None:
            return jsonify("User Email NOT Verified")

        password = post_data.get('password')
        hashed_password = db.session.query(User.password).filter(User.email == post_data.get("email")).first()
        valid_password = bcrypt.check_password_hash(hashed_password[0], password)
        if valid_password:
            return jsonify("User Verfied")
        return jsonify("Password is not correct for this user")
    return jsonify("Error verifying user")

@app.route('/users', methods=['GET'])
def return_all_users():
    all_users = db.session.query(User.id, User.name, User.email, User.password, User.user_type).all()
    return jsonify(all_users)


@app.route('/cart/input', methods = ['POST'])
def cart_input():
    if request.content_type == 'application/json':
       post_data = request.get_json()
       qty = post_data.get('qty')
       total = post_data.get('total')
       user_id = post_data.get("user_id")
       rec = Cart(qty, total)
       db.session.add(rec)    
       db.session.commit()
       return jsonify("Data Posted")

    return jsonify('Something went wrong')

@app.route('/carts', methods=['GET'])
def return_carts():
    all_carts = db.session.query(Cart.id, Cart.qty, Cart.total, Cart.user_id).all()
    return jsonify(all_carts)

@app.route('/cart/<id>', methods=['GET'])
def return_single_cart(id):
    one_cart = db.session.query(Cart.id, Cart.qty, Cart.total, Cart.user_id).filter(Cart.id == id).first()
    return jsonify(one_cart)

@app.route('/cart/delete/<id>', methods=["DELETE"])
def cart_delete(id):
    if request.content_type == 'application/json':
       
        record = db.session.query(Cart).get(id)
        db.session.delete(record)
        db.session.commit()
        return jsonify("Completed Delete action")
    return jsonify("delete failed")

@app.route('/user/delete/<id>', methods=["DELETE"])
def user_delete(id):
    record = db.session.query(User).get(id)
    db.session.delete(record)
    db.session.commit()
    return jsonify('Completed delete user')

@app.route('/single/user/<id>', methods=["GET"])
def return_single_user(id):
    single_user = db.session.query(User.id, User.name, User.email, User.password, User.user_type).filter(User.id == id).first()
    return jsonify(single_user)


# Order Routes
@app.route('/order/input', methods = ['POST'])
def order_input():
    if request.content_type == 'application/json':
       post_data = request.get_json()
       user_id = post_data.get("user_id")
       date = post_data.get('date')
       total = post_data.get('total')
       rec = Order(user_id, date, total)
       db.session.add(rec)    
       db.session.commit()
       return jsonify("Order Posted")
    return jsonify('Something went wrong')


@app.route('/orders', methods=['GET'])
def return_orders():
    all_orders = db.session.query(Order.id, Order.user_id, Order.date, Order.total).all()
    return jsonify(all_orders)


@app.route('/delete/order/<id>', methods=["DELETE"])
def order_delete(id):
    record = db.session.query(Order).get(id)
    db.session.delete(record)
    db.session.commit()
    return jsonify('Completed delete Order')


@app.route('/search/<title>', methods=['GET'])
def goodies_search(title):
    search_goodies = db.session.query(Goodies.id, Goodies.title, Goodies.summary, Goodies.cost, Goodies.goodieType, Goodies.goodie_url).filter(Goodies.title == (title.title())).first()

    return jsonify(search_goodies)

@app.route('/charge', methods=['POST'])
def charge():
    amount = 500

    customer = stripe.Customer.create(
        email='customer@test.com',
        source=request.form['stripeToken']
        )

    charge = stripe.Charge.create(
        customer=customer.id,
        amount=amount,
        currency='usd',
        description='Our Flask Charge'
        )
    return render_template('charge.html', amount=amount)

  

if __name__ == "__main__":
    app.debug = True
    app.run()
