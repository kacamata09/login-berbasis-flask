from flask import Blueprint

userBp = Blueprint('user', __name__, url_prefix='/user')


@userBp.route('/')
def user():
    return


@userBp.route('/edit')
def edit_user():
    return


@userBp.route('/')
def user():
    return
