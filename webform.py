from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from datetime import datetime
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileAllowed, FileField, FileRequired

#create the search form
class SearchForm(FlaskForm):
    searched = StringField('Searched', validators=[DataRequired()])
    submit = SubmitField('Submit')

#create the login form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Submit')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = CKEditorField('Content', validators=[DataRequired()])
    file= FileField('File')
    slug = StringField('Keywords', validators=[DataRequired()])
    submit = SubmitField('Submit')

#create a form class
class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password_hash=PasswordField('Password', validators=[DataRequired(),EqualTo('password_hash2',message= 'Passwords must match')])
    password_hash2=PasswordField('Comfirm Password ', validators=[DataRequired()])
    profile_pic = FileField('Profile Picture')
    submit = SubmitField('Submit')

#create a form class
class NamerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

#create a form class
class PasswordForm(FlaskForm):
    email = StringField('eamil', validators=[DataRequired()])
    password_hash = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class VirtualForm(FlaskForm):
    photo = FileField('Upload Photo', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])
    submit=SubmitField('Use Virtual lab')

class AdminForm(FlaskForm):
        # Liste d'options pour le menu déroulant
    options = [('option1', 'Developer'), ('option2', 'Administrator'), ('option3', 'Expert')]
    dropdown = SelectField("Modify the role of the user:",choices=options)
    submit=SubmitField('Modify')


class ReportForm(FlaskForm):
    text_field = StringField('Text Field')
    submit_button = SubmitField('Submit')