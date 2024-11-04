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

@sio.on('virtual_configuation_change')
def handle_VconfigurationChange(data):
    print(f'received virtual configuration update: {data}')

@sio.on("NewVirtualObject")
def handle_NewVirtualObject(data):
    print("New virtual Object Detected:", data)

@sio.on('physical_configuration_change')
def handle_physicalConfigurationChange(data):
    print(f'received physical configuration update: {data}')




try:
    sio.connect('http://127.0.0.1:5000')
except Exception as e:
    print(f"Connection failed: {e}")
    
sio.wait()

