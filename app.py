from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
import random

NAMES = ['هوشنگ', 'خدای تکلنولوژی', 'کوین میتنیک', 'تری دیویس', 'ایلان ماسک', 'بیل گیتس', 'حاکر ناسا']

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Shayan...'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.String(50), nullable=True)
    time = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=3, minutes=30))


with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')


connected_users = {}


@socketio.on('connect')
def handle_connect():
    name = random.choice(NAMES)
    connected_users[request.sid] = name

    emit('your_name', name)

    messages = Message.query.order_by(Message.time).all()
    history = [
        {
            'text': m.text,
            'time': m.time.strftime('%H:%M'),
            'user_id': m.user_id
        }
        for m in messages
    ]
    emit('history', history)


@socketio.on('disconnect')
def handle_disconnect():
    connected_users.pop(request.sid, None)


@socketio.on('msg')
def handle_msg(data):
    name = connected_users.get(request.sid, 'ناشناس')

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