from wtforms import Form, StringField, PasswordField, validators

class Login(Form):
    user_id = StringField('User ID', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])