from flask.ext.wtf import Form, TextField, TextAreaField, validators, \
    HiddenField, PasswordField
from flask.ext.babel import gettext as _

from app.utils import is_name

class CommentForm(Form):
    name = TextField('Name', [
        validators.Required(),
        validators.Length(min=2, max=50),
        is_name,
    ])
    body = TextAreaField('Comment', [
        validators.Required(),
        validators.Length(min=2, max=510),
    ])
    reply_id = HiddenField('reply_id')
    post_id = HiddenField('post_id')


class PostForm(Form):
    title = TextField('Title', [
        validators.Length(min=0, max=250),
    ])
    body = TextAreaField('Content', [
        validators.Required(),
        validators.Length(min=2, max=1000),
    ])
    tags = TextField('Tags', [
        validators.Required(),
        validators.Length(min=2, max=100),
        is_name,
    ])

class LoginForm(Form):
    username = TextField('username', [
        validators.Required(),
        validators.Length(min=2, max=250),
        is_name,
    ])
    password = PasswordField('password', [
        validators.Required(),
        validators.Length(min=2, max=1000),
    ])
