from wtforms import Form, StringField, validators

class ChangeName(Form):
    new_name = StringField('New Display Name', [validators.DataRequired()])