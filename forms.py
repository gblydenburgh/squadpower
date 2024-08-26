from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    resistance = IntegerField('Resistance', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Save')

    def validate(self, *args, **kwargs):
        # Call the parent class's validate method to ensure full validation is done
        rv = super(UserForm, self).validate(*args, **kwargs)
        if not rv:
            print("Form validation failed.")  # Log if validation fails
        else:
            print("Form validation succeeded.")  # Log if validation succeeds
        return rv
