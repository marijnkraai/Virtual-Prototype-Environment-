from flask_socketio import SocketIO, emit
from api_init import app

#Create a socketyIO connection
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")