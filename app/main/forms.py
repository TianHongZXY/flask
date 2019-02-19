from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    age = IntegerField('How old are you?', validators=[DataRequired()])
    submit = SubmitField('Submit')
