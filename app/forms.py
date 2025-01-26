from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Length, URL

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')

class RegistrationForm(FlaskForm):
    username = StringField('Username', 
        validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password',
        validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password',
        validators=[DataRequired(), EqualTo('password')])

class BotRegistrationForm(FlaskForm):
    bot_token = StringField('Bot Token', 
        validators=[DataRequired(), Length(min=40, max=46)])
    webhook_url = StringField('Webhook URL',
        validators=[DataRequired(), URL()])