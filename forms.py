from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, FieldList, FormField, SelectField
from wtforms.validators import DataRequired, NumberRange

class SquadForm(FlaskForm):
    power = IntegerField('Squad Power', validators=[DataRequired(), NumberRange(min=1, max=500_000_000_000)])

class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    resistance = IntegerField('Resistance', validators=[DataRequired(), NumberRange(min=0)])
    squad_count = SelectField('Number of Squads', choices=[(str(x), str(x)) for x in range(1, 5)], coerce=int)
    submit = SubmitField('Next')  # The first step button to move to the next stage

class SquadInputForm(FlaskForm):
    squads = FieldList(FormField(SquadForm), min_entries=1, max_entries=4)
    submit = SubmitField('Save')

class DeleteForm(FlaskForm):
    submit = SubmitField('Delete')
    
class SearchForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Search')