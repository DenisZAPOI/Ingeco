"""Development launch: python -m app"""

from .config import Config
from .extensions import socketio
from .main import create_app

if __name__ == "__main__":
    application = create_app()
    # socketio.run and not app.run: the server must handle HTTP AND WebSocket.
    socketio.run(
        application,
        host="127.0.0.1",
        port=Config.PORT,
        debug=Config.DEBUG,
        allow_unsafe_werkzeug=True,  # development server only
    )
