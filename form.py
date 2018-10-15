from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from wtforms import StringField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField, PasswordField, BooleanField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
from wtforms_sqlalchemy.fields import QuerySelectField


class Menu(FlaskForm):
    dish = StringField('Dish', validators=[DataRequired()])
    dishprice = StringField('Dish Price', validators=[DataRequired()])
    dishimage = FileField('image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png'], 'Images only!')
    ])
    dishdescription = TextAreaField('Description', validators=[DataRequired()])
    dishoffer = BooleanField('Offer', validators=[DataRequired()])
    dishofferprice = StringField('Offer Price', validators=[DataRequired()])

    # def reset(self):
    #     blankData = MultiDict([ ('csrf', self.reset_csrf() ) ])
    #     self.process(blankData)


class Dessert(FlaskForm):
    desert = StringField('Dessert', validators=[DataRequired()])
    dessertprice = StringField('Dessert Price', validators=[DataRequired()])
    desertimage = FileField('image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png'], 'Images only!')
    ])
    dessertdescription = StringField('Dessert Description', validators=[DataRequired()])
    dessertoffer = BooleanField('Dessert Offer', validators=[DataRequired()])
    dessertofferprice = StringField('Dessert Offer Price', validators=[DataRequired()])

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