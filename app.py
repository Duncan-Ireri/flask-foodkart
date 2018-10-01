import datetime
from flask import Flask, request, render_template, session, url_for, redirect
from flask_babelex import Babel
from flask_sqlalchemy import SQLAlchemy
from flask_user import current_user, login_required, roles_required, UserManager, UserMixin
from flask_admin import Admin
from faker import Faker

# Class-based application configuration
class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'

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
# image-upload settings
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
    __tablename_ = 'maindish'
    id = db.Column(db.Integer, primary_key=True)
    dish = db.Column(db.String(120), nullable=False)
    dishprice = db.Column(db.String(120), nullable=False)
    dishimage = db.Column(db.BLOB)
    dishdescription = db.Column(db.String(200), nullable=False)
    dishoffer = db.Column(db.Boolean(), nullable=False, server_default='0')
    dishofferprice = db.Column(db.String(120))


class DessertDish(db.Model):
    __tablename_ = 'dessertdish'
    id = db.Column(db.Integer, primary_key=True)
    desert = db.Column(db.String(120), nullable=False)
    dessertprice = db.Column(db.String(120), nullable=False)
    desertimage = db.Column(db.BLOB)
    desserttype = db.Column(db.String(200), nullable=False)
    dessertdescription = db.Column(db.String(200), nullable=False)
    dessertoffer = db.Column(db.Boolean(), nullable=False, server_default='0')
    dessertofferprice = db.Column(db.String(120))

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
    page_id = db.Column(db.Integer, db.ForeignKey('pages.id'))
    noticecontent = db.Column(db.String(120), nullable=False)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')
    # User authentication information. The collation='NOCASE' is required
    # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
    username = db.Column(db.String(100, collation='NOCASE'), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')
    email_confirmed_at = db.Column(db.DateTime())
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

# Views
@app.route('/', methods=('GET', 'POST'))
def index():
    if current_user.is_authenticated:
        user = current_user.username + "  : Member"
        return render_template('index.html', user=user)
    else:
        session['username'] = fake.color_name() + fake.last_name() + ": Guest"
        user = session['username']
        return render_template('index.html', user=user)

@app.route('/admin_panel')
@login_required
@roles_required('Admin')
def admin_panel():
	return render_template('admin/admin.html')

@app.route('/additems')
@login_required
@roles_required('Admin')
def additems():
	return render_template('admin/items.html')

@app.route('/catering')
def catering():
	return render_template('catering.html')
# Run
if __name__ == '__main__':
    app.run(debug=True)
