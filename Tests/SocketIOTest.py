from flask import Flask
from flask_socketio import SocketIO, send, emit
from webSocket import socketio

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# Built-in connect event
@socketio.on('connect')
def handle_connect():
    print("A client connected")
    send("Welcome to the server!")

# Built-in disconnect event
@socketio.on('disconnect')
def handle_disconnect():
    print("A client disconnected")

# Default message event
@socketio.on('message')
def handle_message(data):
    print("Message received:", data)
    send(f"Echo: {data}")  # Sends the message back to the client

@socketio.on('create_object')
def create_object(data):
    print("creating object")
    emit('object', {"object": data})

@socketio.on('physical_configuration_change')
def handle_physicalConfigurationChange(data):
    print("New phyiscal Configuration change received:", data)
    



if __name__ == '__main__':
    socketio.run(app, debug=True)
