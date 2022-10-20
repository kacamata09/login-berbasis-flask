from flask import Blueprint

loginBp = Blueprint('login', __name__, url_prefix='/login')


@loginBp.route('/')
def login():
    return
