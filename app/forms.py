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

from wtforms import SelectField

class BotRegistrationForm(FlaskForm):
    bot_token = StringField('Bot Token', 
        validators=[DataRequired(), Length(min=40, max=46)])
    bot_type = SelectField('Bot Type',
        choices=[
            ('number_converter', 'Number Converter Bot'),
            ('dice_mmo', 'Dice MMO Game Bot')
        ],
        validators=[DataRequired()])
    webhook_url = StringField('Webhook URL',
        validators=[DataRequired(), URL()])
    config = StringField('Additional Configuration (JSON)',
        description='Optional JSON configuration for the bot')