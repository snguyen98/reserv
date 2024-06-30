from wtforms import Form, PasswordField, validators

class ResetPassword(Form):
    new_pass = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm_pass', message='Passwords must match')
    ])
    confirm_pass = PasswordField('Confirm password')