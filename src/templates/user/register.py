from flask import Blueprint

registerBp = Blueprint('register', __name__, url_prefix='/register')


@registerBp.route('/')
def register():
    return
