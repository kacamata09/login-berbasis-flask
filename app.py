from importlib.metadata import requires
from threading import Thread
from flask import Flask, request, jsonify, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, logout_user, login_required, current_user
from flask_mail import Mail, Message
from werkzeug.security import check_password_hash


# library pendukung
from datetime import datetime, timedelta
import jwt
from random import randint
from functools import wraps

# init
app = Flask(__name__)

# variabel
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///loginrole.db'
app.config['SECRET_KEY'] = 'hacker jangan menyerang'
dbku = SQLAlchemy(app)

# email
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = "muh.ansharazhari@gmail.com"
app.config['MAIL_PASSWORD'] = "mvhmlommxlosyynb"
mail = Mail(app)


# middleware atau decorator required
# login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# akses admin
def akses_admin(fungsi):
    @wraps(fungsi)
    def kunci_halaman(*args, **kwargs):
        username = current_user.username
        siUser = Pengguna.query.filter_by(username=username).first()
        if siUser.role.hak_akses == 'admin':
            return fungsi(*args, **kwargs)
        elif siUser.role.hak_akses == 'user':
            return 'anda adalah user tidak bisa mengakses halaman ini'
        else:
            return 'sepertinya data anda ada yang salah'
    return kunci_halaman


@login_manager.user_loader
def load_user(id):
    try:
        return Pengguna.query.get(int(id))
    except:
        return 'maaf anda harus login dulu <a href="/">Login</a>'

# models


class Pengguna(dbku.Model, UserMixin):
    id = dbku.Column(dbku.Integer, primary_key=True)
    email = dbku.Column(dbku.String(255), unique=True)
    username = dbku.Column(dbku.String(255), unique=True)
    password = dbku.Column(dbku.String(255))
    id_akses = dbku.Column(dbku.Integer, dbku.ForeignKey('roles.id'))


class Roles(dbku.Model):
    id = dbku.Column(dbku.Integer, primary_key=True)
    hak_akses = dbku.Column(dbku.String(255))
    user_id = dbku.relationship('Pengguna', backref='role')


# routes sekaligus controllers
@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        siUser = Pengguna.query.filter_by(username=username).first()
        if siUser:
            if siUser.password == password:
                print(siUser)
                login_user(siUser)

                # token = jwt.encode(
                #     {'username': username, 'exp': datetime.now() + timedelta(days=1)})
                # if request.args.get('next'):
                #     return redirect(request.args.get("next"))
                return redirect(url_for('index'))
                # return redirect(url_for("index", next=request.url))
            return 'maaf password yang anda masukkan salah'

        return 'Maaf username yang anda masukkan tidak ada'
    return render_template('login.html')


@ app.route('/logout')
@ login_required
def logout():
    logout_user()
    return 'selamat anda berhasil logout'


@ app.route('/register', methods=['GET', 'POST'])
@ login_required
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        pengguna_baru = Pengguna(
            username=username, email=email, password=password, id_akses=role)
        dbku.session.add(pengguna_baru)
        dbku.session.commit()
        return 'selamat anda berhasil menambahkan pengguna'
    return render_template('register.html')


@ app.route('/role', methods=['GET', 'POST'])
def role():
    if request.method == 'POST':
        role = request.form.get('role')
        role_baru = Roles(hak_akses=role)
        dbku.session.add(role_baru)
        dbku.session.commit()
        return 'selamat anda berhasil menambahkan role'
    return render_template('role.html')


@ app.route('/admin')
@ login_required
@ akses_admin
def halaman_admin():
    return 'ini adalah halaman admin, jika anda berhasil mengakses nya berarti anda adalah admin'


@app.route('/user')
def tampilUser():
    users = Pengguna.query.all()
    return render_template('user.html', users=users)


def send_email(app, msg):
    with app.app_context():
        mail.send(msg)


@app.route('/resetpassword', methods=['POST', 'GET'])
def reset():
    if request.method == 'POST':
        msg = Message()
        msg.subject = "Reset Password Anda"
        siUser = Pengguna.query.filter_by(
            email=request.form.get('email')).first()
        if siUser:
            email_penerima = siUser.email
            msg.recipients = [email_penerima]
            msg.sender = 'muh.ansharazhari@gmail.com'
            kode_reset = jwt.encode(
                {'email': email_penerima, 'exp': datetime.now() + timedelta(minutes=2)}, email_penerima, algorithm='HS256')
            # kode_reset = randint(1, 9999)
            msg.body = f'Kode reset password anda adalah {kode_reset}'
            mail.send(msg)
            return 'tunggu kode anda di email anda'
        return 'email anda tidak terdaftar di aplikasi'
    # Thread(target=send_email, args=(app, msg)).start()
    return render_template('verifikasireset.html')


@app.route('/kodereset', methods=['GET', 'POST'])
def kode_reset():
    if request.method == 'POST':
        kode_reset = request.form.get('kode')
        try:
            jwt.decode(kode_reset, request.form.get(
                'email'), algorithms=['HS256'])
        except:
            return 'email atau token yang anda masukkan salah'
        siUser = Pengguna.query.filter_by(
            email=request.form.get('email')).first()
        siUser.password = request.form.get('password_baru')
        dbku.session.commit()
        # return redirect('/ubahpassword')
        return 'selamat password anda berhasil diubah'
    return render_template('resetpassword.html')


@app.route('/ubahpassword', methods=['GET', 'POST'])
def ubah_password():
    if request.method == 'POST':
        email_user = request.args.get('email')

    return render_template('reset_password.html')


if __name__ == '__main__':