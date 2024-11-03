import socketio

# Initialize a Socket.IO client
sio = socketio.Client()

# Built-in connect event handler
@sio.event
def connect():
    print("Connected to the server")
    sio.emit('create_object', {"object_id": 1})

# Built-in disconnect event handler
@sio.event
def disconnect():
    print("Disconnected from the server")

# Default message event handler
@sio.event
def message(data):
    print("Message from server:", data)

@sio.on('configuration_update')
def handle_configurationUpdate(data):
    print('Received new configuration update:', data)

@sio.on('virtual_configuation_change')
def handle_configurationChange(data):
    print(f'received virtual configuration update: {data}')

try:
    sio.connect('http://127.0.0.1:5000')
except Exception as e:
    print(f"Connection failed: {e}")
    
sio.wait()

