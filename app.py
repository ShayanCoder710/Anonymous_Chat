from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
import hashlib
import secrets

MAX_LEN = 500
MAX_NAME_LEN = 30

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Shayan...'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(MAX_LEN), nullable=False)
    user_id = db.Column(db.String(MAX_NAME_LEN), nullable=True)
    time = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=3, minutes=30))


class Name(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(MAX_NAME_LEN), unique=True, nullable=False)
    token_hash = db.Column(db.String(64), nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')


connected_users = {}


def hash_token(token):
    return hashlib.sha256(token.encode('utf-8')).hexdigest()


def valid_name(name):
    name = name.strip()
    return 1 <= len(name) <= MAX_NAME_LEN


def send_history(sid):
    messages = Message.query.order_by(Message.time).all()
    history = [
        {
            'text': m.text,
            'time': m.time.strftime('%H:%M'),
            'user_id': m.user_id
        }
        for m in messages
    ]
    emit('history', history, to=sid)


@socketio.on('claim_name')
def handle_claim_name(data):
    if not isinstance(data, dict):
        return

    name = data.get('name', '')
    token = data.get('token')

    if not isinstance(name, str) or (token is not None and not isinstance(token, str)):
        return

    if not valid_name(name):
        emit('claim_error', 'نام باید بین ۱ تا ۳۰ کاراکتر باشد.')
        return

    if token:
        known = Name.query.filter_by(token_hash=hash_token(token)).first()

        if known:
            connected_users[request.sid] = known.name
            emit('name_ok', {'name': known.name, 'token': None})
            send_history(request.sid)
            socketio.emit('online_count', len(connected_users))
            return

    if Name.query.filter_by(name=name).first():
        emit('claim_error', 'این نام قبلاً استفاده شده. یک نام دیگر انتخاب کنید.')
        return

    new_token = secrets.token_urlsafe(32)
    db.session.add(Name(name=name, token_hash=hash_token(new_token)))
    db.session.commit()

    connected_users[request.sid] = name
    emit('name_ok', {'name': name, 'token': new_token})
    send_history(request.sid)
    socketio.emit('online_count', len(connected_users))


@socketio.on('connect')
def handle_connect():
    emit('online_count', len(connected_users))


@socketio.on('disconnect')
def handle_disconnect():
    connected_users.pop(request.sid, None)

    socketio.emit('online_count', len(connected_users))


@socketio.on('msg')
def handle_msg(data):
    name = connected_users.get(request.sid, 'ناشناس')

    if not isinstance(data, str) or len(data) > MAX_LEN:
        return

    data = data.strip()

    if not data:
        return

    new_msg = Message(text=data, user_id=name)
    db.session.add(new_msg)
    db.session.commit()

    emit('msg', {
        'text': data,
        'time': new_msg.time.strftime('%H:%M'),
        'user_id': name
    }, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, debug=True)