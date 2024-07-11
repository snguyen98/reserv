from wtforms import Form, StringField, validators

class ChangeName(Form):
    """
    Form definition for change display name page
    """
    new_name = StringField('New Display Name', [validators.DataRequired()])