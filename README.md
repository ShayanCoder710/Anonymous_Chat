# Anonymous Chat

A real-time anonymous chat built with Flask and Socket.IO. Each user picks a name on first visit, and messages are delivered instantly to everyone currently online.

## Features

- **Real-time messaging** — messages broadcast to all connected users, no refresh needed
- **Permanent names** — the name is stored server-side and can never be changed or claimed again, even if the user clears their browser's localStorage. Only the original owner can reclaim it, via a secret token
- **Online counter** — live count of connected users in the header
- **Message history** — all messages persisted in SQLite and replayed on reconnect
- **500 character limit** on messages, enforced client- and server-side
- **Enter** sends a message, **Shift+Enter** adds a newline

## Stack

Flask 3.1.3 · Flask-SocketIO 5.6.1 · Flask-SQLAlchemy 3.1.1 · SQLAlchemy 2.1.2 · SQLite

The frontend is plain HTML/CSS/JS with no framework; the Socket.IO client loads from a CDN.

## Running

```bash
pip install flask flask-socketio flask-sqlalchemy
flask --app app run
```

Then open `http://127.0.0.1:5000`. Tables are created automatically on first run.
