import datetime, os
from flask import Flask, request, render_template, session, url_for, redirect, flash
from flask_babelex import Babel
from flask_sqlalchemy import SQLAlchemy

from flask_user import current_user, login_required, roles_required, UserManager, UserMixin
from flask_admin import Admin
from faker import Faker
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from wtforms import StringField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField, PasswordField, BooleanField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
from wtforms_sqlalchemy.fields import QuerySelectField
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

# Class-based application configuration
class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'
    #SQLALCHEMY_DATABASE_URI = "mysql://{username}:{password}@{hostname}/{databasename}".format(
#    username="root",
#    password="root",
#    hostname="localhost",
#    databasename="pages" )
    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///food.db'    # File-based SQL database
    SQLALCHEMY_TRACK_MODIFICATIONS = False    # Avoids SQLAlchemy warning

    # Flask-Mail SMTP server settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = 'email@example.com'
    MAIL_PASSWORD = 'password'
    MAIL_DEFAULT_SENDER = '"MyApp" <noreply@example.com>'

    # Flask-User settings
    USER_APP_NAME = "FOODKART"      # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = False        # Enable email authentication
    USER_ENABLE_USERNAME = True # Disable username authentication
    USER_EMAIL_SENDER_NAME = USER_APP_NAME
    USER_EMAIL_SENDER_EMAIL = "noreply@example.com"

    
    # Create Flask app load app.config
app = Flask(__name__)

# app.config.from_pyfile('flask.cfg')
# image-upload settings
# UPLOAD_FOLDER = 'static/uploads'
# ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure the image uploading via Flask-Uploads
app.config['UPLOADED_PHOTOS_DEST'] = 'uploads/'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app) # set maximum file size, default is 16MB

app.config.from_object(__name__+'.ConfigClass')
# Initialize Flask-BabelEx
babel = Babel(app)
# Initialize Flask-SQLAlchemy
db = SQLAlchemy(app)

# faker init

fake = Faker()

# Define the User data-model.
# NB: Make sure to add flask_user UserMixin !!!

class MainDish(db.Model):
    __tablename_ = 'main_dish'
    id = db.Column(db.Integer, primary_key=True)
    dish = db.Column(db.String(120), nullable=False)
    dishtype = db.Column(db.String(120), nullable=False)
    dishprice = db.Column(db.String(120), nullable=False)
    dish_filename = db.Column(db.String, default=None, nullable=True)
    dish_url = db.Column(db.String, default=None, nullable=True)
    dishdescription = db.Column(db.String(200), nullable=False)
    # dishoffer = db.Column(db.Boolean(), nullable=False, server_default='0')
    # dishofferprice = db.Column(db.String(120))
    cart = db.relationship('FoodCart', backref='menu', lazy='dynamic')

class Pages(db.Model):
    __tablename__ = 'pages'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(1000))
    content = db.Column(db.BLOB)

    def __init__(self, title, content):
        self.title = title
        self.content = content

    def __repr__(self):
        return '<Pages : id=%r, title=%s, content=%s>' % (self.id, self.title, self.content)

class Notice(db.Model):
    __tablename_ = 'notice'

    id = db.Column(db.Integer, primary_key=True)
    notice = db.Column(db.String(120), nullable=False)
    noticecontent = db.Column(db.String(120), nullable=False)

class FoodCart(db.Model):
    __tablename__ = 'foodcart'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(120), nullable=True)
    menu_id = db.Column(db.Integer, db.ForeignKey('main_dish.id'))
    main_dish = db.relationship("MainDish")


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')
    # User authentication information. The collation='NOCASE' is required
    # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
    username = db.Column(db.String(100, collation='NOCASE'), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')
    email_confirmed_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    # email_confirmed_at = db.Column(db.DateTime(datetime.datetime.now()))

    # User information
    first_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
    last_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
    # Define the relationship to Role via UserRoles
    roles = db.relationship('Role', secondary='user_roles')
# Define the Role data-model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
# Define the UserRoles association table
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))

    # Setup Flask-User and specify the User data-model
user_manager = UserManager(app, db, User)

    # Create all database tables
db.create_all()

    # Create 'member@example.com' user with no roles
if not User.query.filter(User.username == 'member').first():
    user = User(
        username='member',
        email_confirmed_at=datetime.datetime.utcnow(),
        password=user_manager.hash_password('Password1'),
    )
    db.session.add(user)
    db.session.commit()

    # Create 'admin@example.com' user with 'Admin' and 'Agent' roles
if not User.query.filter(User.username == 'droidthelast').first():
    user = User(
        username='droidthelast',
        email_confirmed_at=datetime.datetime.utcnow(),
        password=user_manager.hash_password('Password1'),
    )
    user.roles.append(Role(name='Admin'))
    user.roles.append(Role(name='Agent'))
    db.session.add(user)
    db.session.commit()


# forms
class Menu(FlaskForm):
    dish = StringField('Dish', validators=[DataRequired()])
    dishprice = StringField('Dish Price', validators=[DataRequired()])
    dishtype = SelectField(
        "Dish type",
        choices = [('Main course', 'main'), ('Dessert', 'dessert'), ('Juices', 'juice'), ('Cake', 'cake'), ('Vegan', 'vegan'), ('Soup', 'soup')]
    )
    dishimage = FileField('image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')
    ])
    dishdescription = TextAreaField('Description', validators=[DataRequired()])
    # dishoffer = BooleanField('Offer', validators=[DataRequired()])
    # dishofferprice = StringField('Offer Price', validators=[DataRequired()])
    submit = SubmitField(u'Upload')
    # def reset(self):
    #     blankData = MultiDict([ ('csrf', self.reset_csrf() ) ])
    #     self.process(blankData)


class PageForm(FlaskForm):
    title = StringField('Pages', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])


class NoticeForm(FlaskForm):
    notice = StringField('Notice', validators=[DataRequired()])
    noticecontent = StringField('Content', validators=[DataRequired()])

    # def __init__ (self):
    #     super (NoticeForm, self). __init__()
    #     self.page_id.choices = [(c.id, c.title) for c in Pages.query.all()]
    # 

# Views
@app.route('/', methods=('GET', 'POST'))
def index():

    maindish = MainDish.query.filter_by(dishtype='Main course').all()
    juicedish = MainDish.query.filter_by(dishtype='Juices').all()
    if current_user.is_authenticated:
        cart_user = current_user.username
        sic = FoodCart.query.filter_by(user=cart_user)
        items = [row.menu_id for row in sic.all()]
        session['cart'] = items
        return render_template('index.html', user=cart_user, maindish=maindish, juicedish=juicedish, sic=session['cart'])
    else:
        session['username'] = fake.color_name() + fake.last_name() + ": Guest"
        user = session['username']
        return render_template('index.html', user=user, maindish=maindish, juicedish=juicedish)


@app.route('/admin_panel')
@login_required
@roles_required('Admin')
def admin_panel():
	return render_template('admin/admin.html')


@app.route('/dish_add')
@login_required
@roles_required('Admin')
def dish_add():
    form = Menu()
    return render_template('admin/dish.html', form=form)


@app.route('/dish', methods=['POST', 'GET'])
@login_required
def dish():
    form = Menu()

    if request.method == 'POST':
        if form.validate_on_submit():
            filename = photos.save(request.files['dishimage'])
            url = photos.url(filename)
            new_dish = MainDish(dish=form.dish.data, dishprice=form.dishprice.data, dishtype=form.dishtype.data, dishdescription=form.dishdescription.data, dish_filename=filename, dish_url=url)
            db.session.add(new_dish)
            db.session.commit()
            flash('New Dish, {}, added!'.format(new_dish.dish), 'success')
            return redirect(url_for('admin_panel'))
        else:
            flash_errors(form)
            flash('ERROR! Dish was not added.', 'error')
 
    return render_template('admin/dish.html', form=form)

@app.route("/add_to_cart/<int:id>")
def add_to_cart(id):
    """TODO: Finish shopping cart functionality using session variables to hold
    cart list.

    Intended behavior: when a dish is added to a cart, redirect them to the
    shopping cart page, while displaying the message
    "Successfully added to cart" """

    if "cart" not in session:
        session["cart"] = []

    session["cart"].append(id)
    iog = id
    if current_user.is_authenticated:
        user = current_user.username
        new_cart = FoodCart(user=user, menu_id=iog)
        db.session.add(new_cart)
        db.session.commit()    

        flash("Successfully added to cart!" + user)
        return redirect("/cart")
    else: 
        return redirect("/user/sign-in")
        # guest_user = session['username']
        # new_guest_cart = FoodCart(user=guest_user, menu_id=iog)
        # db.session.add(new_guest_cart)
        # db.session.commit()    

        # flash("Successfully added to cart!" + guest_user)
        # return redirect("/guest_cart")


@app.route("/cart")
def shopping_cart():
    """TODO: Display the contents of the shopping cart. The shopping cart is a
    list held in the session that contains all the dishes to be added. Check
    accompanying screenshots for details."""
    if "cart" not in session:
        flash("There is nothing in your cart.")
        return render_template("cart.html", display_cart = {}, total = 0)
    else:
        items = session['cart']

        dict_of_dishes = {}

        total_price = 0
        for item in items:
            dis = MainDish.query.filter(item).all()
            total_price += dis.dishprice
            if dis.id in dict_of_dishes:
                dict_of_dishes[dis.id]["qty"] += 1
            else:
                dict_of_dishes[dis.id] = {"qty":1, "name": dis.dish, "price":dis.dishprice}
        
        return render_template("cart.html", display_cart = dict_of_dishes, total = total_price)  

@app.route('/catering')
def catering():
	return render_template('catering.html')
# RunSS
if __name__ == '__main__':
    app.run(debug=True)
