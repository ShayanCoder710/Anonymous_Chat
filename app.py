from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ShayanShayan810818081081081018108ShayanShayan0283594890889023480843842098398&7'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    time = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=3, minutes=30))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    messages = Message.query.order_by(Message.time).all()
    history = [{'text': m.text, 'time': m.time.strftime('%H:%M')} for m in messages]
    emit('history', history)

@socketio.on('disconnect')
def handle_disconnect():
    pass

@socketio.on('msg')
def handle_msg(data):    
    new_msg = Message(text=data)
    db.session.add(new_msg)
    db.session.commit()

    emit('msg', {
        'text': data,
        'time': new_msg.time.strftime('%H:%M')
    }, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)