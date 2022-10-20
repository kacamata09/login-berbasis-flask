from flask import Blueprint

userBp = Blueprint('kodereset', __name__, url_prefix='/kode_reset')


@userBp.route('/')
def user():
    return
