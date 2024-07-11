from wtforms import Form, StringField, PasswordField, validators

class Login(Form):
    """
    Form definition for login page
    """
    user_id = StringField('User ID', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])