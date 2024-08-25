from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, FieldList, FormField
from wtforms.validators import DataRequired, NumberRange

class SquadForm(FlaskForm):
    power = IntegerField('Squad Power', validators=[DataRequired(), NumberRange(min=0)])

class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    resistance = IntegerField('Resistance', validators=[DataRequired(), NumberRange(min=0)])
    squads = FieldList(FormField(SquadForm), min_entries=1, max_entries=4)
    submit = SubmitField('Save')

class SearchForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Search')
