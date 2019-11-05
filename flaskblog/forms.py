# First create form here and then import it into the routes.py

from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskblog.models import User


# This is not like writing regular HTML pages for a form. This is a little different. In this we
# create python classes for each form which are then implicitly converted into HTML pages.
class RegistrationForm(FlaskForm):
    # For validating the fields we use validators. Eg: username should not be empty and should be only
    # 2 to 50 characters long

    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirmPassword = PasswordField('Confirm Password', validators=[DataRequired(),
                                                                    EqualTo('password')])
    submit = SubmitField('Sign Up')

    # We can create a custom validation by simply creating a function for it. Check it out in
    # wt_forms documentation pages.
    def validate_username(self, username):
        # Check out the SQLAlchemy queries on tutorials point
        user = User.query.filter_by(username=username.data).first()
        # If user does not exist user = None
        if user:
            raise ValidationError('That username is taken. Choose a unique one. Preferably your email.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Please enter a unique Email Id')

# For anyone wondering how validate_username() and validate_email() are being called,
# these functions are called with the FlaskForm class that our RegistrationForm class inherited
# from. If you look at the definition for validate_on_submit(), and from there, the definition
# for validate(), that validate function contains the following line:
#
# inline = getattr(self.__class__, 'validate_%s' % name, None)
#
# There is a lot going on in the background, but from what I can tell,
# Flask is checking for extra functions created with the
# naming pattern: "validate_(field name)", and later calling those extra functions.


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    # Will be implemented using cookies
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    # If you want to work with images watch CoreySchafer's 7th video on flask tutorials
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update')

    # The error should be thrown only when the user submits a value which is different from the
    # current values. Otherwise it would still throw an error as the current credentials would
    # be available in the database and it is possible that the user submits the form with the
    # same credentials
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Choose a unique one. Preferably your email.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Please enter a unique Email Id')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')


# For forgot password
class RequestResponseForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        # If user has not created an account but tries to reset password
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('No account with that email.Please create an account first!')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirmPassword = PasswordField('Confirm Password', validators=[DataRequired(),
                                                                    EqualTo('password')])
    submit = SubmitField('Reset Password')
