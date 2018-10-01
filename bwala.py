import datetime, os
import random, string
from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from form import helpForm, LoginForm
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
from create_user import *
from flask_bcrypt import Bcrypt

# import flask_whooshalchemy as wa

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'dfdjdnfbvhfbgjfnjdb'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://duncantricom:simplepass@duncantricom.mysql.pythonanywhere-services.com/duncantricom$bwala-faq'
basedata = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedata, 'faq.db')
#SQLALCHEMY_DATABASE_URI = "mysql://{username}:{password}@{hostname}/{databasename}".format(
#    username="root",
#    password="root",
#    hostname="localhost",
#    databasename="pages" )
#SQLALCHEMY_DATABASE_URI = "mysql+mysqldb://{username}:{password}@{hostname}/{databasename}".format(
#    username="duncantricom",
#    password="Bwaladb",
#    hostname="duncantricom.mysql.pythonanywhere-services.com",
#    databasename="duncantricom$bwala",
#)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['CSRF_ENABLED'] = True
app.config['USER_ENABLE_EMAIL'] = False
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# app.config['WHOOSH_BASE'] = 'whoosh'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


class User(db.Model):
    """An admin user capable of viewing reports.

      :param str email: email address of user
      :param str password: encrypted password for the user

      """
    __tablename__ = 'user'

    email = db.Column(db.String(90), primary_key=True)
    password = db.Column(db.String(250))
    authenticated = db.Column(db.Boolean, default=False)

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.email

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False


class Pages(db.Model):
    __tablename__ = 'pages'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(1000))
    content = db.Column(db.BLOB)

    def __init__(self, title, content):
        self.title = title
        self.content = content

    def __repr__(self):
        return '<Pages : id=%r, title=%s, content=%s>' \
               % (self.id, self.title, self.content)


class Req(db.Model):
    __tablename__ = 'requirements'

    id = db.Column(db.Integer, primary_key=True)
    req_title = db.Column(db.String(1000))
    req_content = db.Column(db.BLOB)

    def __init__(self, req_title, req_content):
        self.req_title = req_title
        self.req_content = req_content

    def __repr__(self):
        return '<Pages : id=%r, req_title=%s, req_content=%s>' \
               % (self.id, self.req_title, self.req_content)


class helpData(db.Model):
    __tablename__ = 'help_table_db'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    tel = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    issue = db.Column(db.String(255), nullable=False)
    report = db.Column(db.String(1000), nullable=False)
    help_no = db.Column(db.String(255), unique=True, nullable=False)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    status = db.Column(db.Boolean(), server_default='0')

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.init_app(app)


@login_manager.user_loader
def user_loader(user_id):
    """Given *user_id*, return the associated User object.

      :param unicode user_id: user_id (email) user to retrieve

      """
    return User.query.get(user_id)


@app.route("/login", methods=["GET", "POST"])
def login():
    """For GET requests, display the login form.
      For POSTS, login the current user by processing the form.

      """
    print ("db")

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.get(form.email.data)
        if user:

            if bcrypt.check_password_hash(user.password, form.password.data):
                user.authenticated = True
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=True)
                return redirect(url_for("admin"))
    return render_template("login.html", form=form)


@app.route("/logout", methods=["GET"])
@login_required
def logout():

    """Logout the current user."""
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return render_template("logout.html")


@app.route('/', methods=['POST', 'GET'])
def faq():
    pages = db.session.query(Pages).all()
    requirements = db.session.query(Req).all()
    return render_template('faq.html', pages=pages, requirements=requirements)


@app.route('/page/<int:page_id>')
def view_page(page_id):
    page = db.session.query(Pages).filter_by(id=page_id).first()
    return render_template('page.html',
                           id=page.id, title=page.title, content=page.content)


@app.route('/edit-page/<int:page_id>')
@login_required
def edit_page(page_id):
    page = db.session.query(Pages).filter_by(id=page_id).first()
    return render_template('edit-page.html',
                           id=page.id, title=page.title, content=page.content)


@app.route('/update-page/', methods=['POST'])
@login_required
def update_page():
    page_id = request.form['id']
    title = request.form['title']
    content = request.form['content']
    db.session.query(Pages).filter_by(id=page_id).update({'title': title.encode('ascii'),
                                                       'content': content.encode('ascii')})
    db.session.commit()
    return redirect('/page/' + page_id)


@app.route('/new-page/')
@login_required
def new_page():
    return render_template('new_faq.html')


@app.route('/test')
@login_required
def test():
    return 'test flask user'


@app.route('/save-page/', methods=['POST'])
@login_required
def save_page():
    page = Pages(title=request.form['title'].encode('ascii'), content=request.form['content'].encode('ascii'))
    db.session.add(page)
    db.session.commit()
    return redirect('/page/%d' % page.id)


@app.route('/delete-page/<int:page_id>')
@login_required
def delete_page(page_id):
    db.session.query(Pages).filter_by(id=page_id).delete()
    db.session.commit()
    return redirect('/')


@app.route('/new-req-page/')
@login_required
def new_req_page():
    return render_template('new_faq_req.html')


@app.route('/save_req_page/', methods=['POST'])
def save_req_page():
    requirements = Req(req_title=request.form['req_title'].encode('ascii'),
                       req_content=request.form['req_content'].encode('ascii'))
    db.session.add(requirements)
    db.session.commit()
    return redirect('/view_req_page/%d' % requirements.id)


@app.route('/view_req_page/<int:req_id>')
def view_req_page(req_id):
    req = db.session.query(Req).filter_by(id=req_id).first()
    return render_template('req_page.html',
                           id=req.id, req_title=req.req_title, req_content=req.req_content)


@app.route('/delete_req_page/<int:req_id>')
@login_required
def delete_req_page(req_id):
    db.session.query(Req).filter_by(id=req_id).delete()
    db.session.commit()
    return redirect('/')


@app.route('/edit_req_page/<int:req_id>')
@login_required
def edit_req_page(req_id):
    req = db.session.query(Req).filter_by(id=req_id).first()
    return render_template('edit_req_page.html',
                           id=req.id, req_title=req.req_title, req_content=req.req_content)


@app.route('/update_req_page/', methods=['POST'])
@login_required
def update_req_page():
    req_id = request.form['id']
    req_title = request.form['req_title']
    req_content = request.form['req_content']
    db.session.query(Req).filter_by(id=req_id).update({'req_title': req_title.encode('ascii'),
                                                       'req_content': req_content.encode('ascii')})
    db.session.commit()
    return redirect('/req_page/' + req_id)

@app.route('/admin')
@login_required
def admin():
    return render_template('admin.html')


@app.route('/help', methods=['GET', 'POST'])
def help():
    form = helpForm()

    if request.method == 'GET':
        return render_template('help.html', form=form)
    elif request.method == 'POST' and form.validate():
        help_no = ''.join(
            random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
        help_data = helpData(name=form.name.data, tel=form.tel.data, email=form.email.data, location=form.location.data,
                             issue=form.issue.data, report=form.report.data, help_no=help_no)

        db.session.add(help_data)
        db.session.commit()

        flash(
            'Hi ' + form.name.data + ' ticket : ' + help_no + ' , one of our representatives will get back to you soon')
    return render_template('thanks.html')


if __name__ == '__main__':
    app.run()



from flask_wtf import FlaskForm
from wtforms import TextField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField, PasswordField
from wtforms import validators, ValidationError

class helpForm(FlaskForm):
    
    """
    Help form for Partners: To be accessed through the partners FAQ pages.
    """
    name = TextField("Name", [validators.Required("Enter Your Name")])
    tel = TextField("Phone", [validators.Required("Phone Number?")])
    email = TextField("Email", [validators.Required("Email"), validators.email("Enter Correct email")])
    location = TextField("Your Locale", [validators.Required("Location")])
    issue = SelectField('Issue', choices=[('service', 'Service'), ('accident', 'Accident'), ('registration', 'Registration'), ('availability', 'Availabilty'), ('account', 'Account')])
    report = TextAreaField('Report')

    def reset(self):
        blankData = MultiDict([ ('csrf', self.reset_csrf() ) ])
        self.process(blankData)

class LoginForm(FlaskForm):
    
    """
    Login form for Partners: To be used before editing stuff first.
    """

    email = TextField("Email", [validators.Required("Email"), validators.email("Enter Correct email")])
    password = PasswordField('Password', [validators.DataRequired()])
