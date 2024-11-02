

from db_config import DATABASE_URL, WS_SECRETKEY, API_BASEURI
from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
#from flask_socketio import SocketIO, emit
from sqlalchemy import select
from models import PhysicalObject, Configuration, VirtualObjectConfiguration, VirtualObject, PhysicalObjectConfiguration, Product # Import the common model
from db_connect import Base, session, engine
import json


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
#app.config['SECRET_KEY'] = WS_SECRETKEY #TODO, add own secret key

# Create a db instance
db = SQLAlchemy(app)

#Create a socketyIO connection
#socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/resetDB', methods = ['DELETE'])
def resetDB():
    try:
        # Drop all tables and recreate them (this will delete all data)
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

        return jsonify({"message": "All data cleared successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#@socketio.on('connect')
#def handle_connect():
    #print('A client connected via WebSocket')

#@socketio.on('disconnect')
#def handle_disconnect():
    #print('A client disconnected from WebSocket')

@app.route('/products', methods = ['POST'])
def add_product():
    #add a new product
    data = request.json

    # Convert data if it’s not a dictionary
    if isinstance(data, str):
        data = json.loads(data)

    # Basic validation to ensure required fields are provided
    if 'product_name' not in data or 'current_config' not in data:
        abort(400, description="Missing product_name or missing current_config")
    
    #Create new virtual object
    new_Product = Product(product_name = data['product_name'], current_config = data['current_config'])

    # Add and commit the new object to the session
    db.session.add(new_Product)
    db.session.commit()
    
    return jsonify(new_Product.to_dict()), 201  # Return the created object

@app.route('/configurations', methods = ['POST'])
def add_configuration():
    print("making configuration")
    #add a new configuration'
    data = request.json
    print(data)
    print(type(data))

    # Basic validation to ensure required fields are provided
    if not isinstance(data, dict) or 'config_type' not in data or 'config_name' not in data:
        abort(400, description="Missing config_type or config_name")

    #Add new configuration to DB
    print("Data received:", data)
    print("Data type:", type(data))
    new_configuration = Configuration(config_type = data['config_type'], config_name = data['config_name'])
    db.session.add(new_configuration)
    db.session.commit()

    # Broadcast the update to all WebSocket-connected clients
    #socketio.emit('configuration_update', data)
    
    return jsonify(new_configuration.to_dict()), 201  # Return the created object

@app.route('/virtual_objects', methods = ['POST'])
def add_virtual_object():
    #add a new virtual Object 
    data = request.json

    # Basic validation to ensure required fields are provided
    if 'object_name' not in data:
        abort(400, description="Missing object_name")
    
    #Create new virtual object
    new_VirtualObject = VirtualObject( object_name = data['object_name'])

    # Add and commit the new object to the session
    db.session.add(new_VirtualObject)
    db.session.commit()
    
    return jsonify(new_VirtualObject.to_dict()), 201  # Return the created object

@app.route('/virtual_objects/<int:id>', methods=['GET'])
def get_physical_object(id):
    """Retrieve a single Virtual object by ID."""
    # Retrieve the object by ID
    virtual_object = db.session.query(VirtualObject).get(id)
    
    # Check if the object exists
    if not virtual_object:
        abort(404, description="Virtual Object not found")
    
    # Convert the object to a dictionary format for JSON serialization
    return jsonify(virtual_object.to_dict()), 201  # Assuming to_dict() is implemented in your model

@app.route('/virtual_configurations', methods = ['POST'])
def add_virtual_configuration():
    #add a new virtual Object 
    data = request.json
    print(data)

    # Basic validation to ensure required fields are provided
    if 'virtual_object_id' not in data or 'config_id' not in data or 'x_coordinate' not in data or 'y_coordinate' not in data:
        abort(400, description="Missing virtual_object_id, config_id, x_coordinate or y_coordinate ")
    
    #Create new virtual object
    new_VirtualConfiguration = VirtualObjectConfiguration(virtual_object_id = data['virtual_object_id'], config_id = data['config_id'], x_coordinate = data['x_coordinate'], y_coordinate = data['y_coordinate'])

    # Add and commit the new object to the session
    db.session.add(new_VirtualConfiguration)
    db.session.commit()

    return jsonify(new_VirtualConfiguration.to_dict()), 201  # Return the created object

@app.route('/physical_objects', methods=['POST'])
def add_physical_object():
    """Add a new physical object."""
    data = request.json

    if 'virtual_object_id' not in data or 'object_name' not in data or 'marker_id' not in data:
        abort(400, description="Missing virtual_object_id, object_name or marker_id ")

    new_object = PhysicalObject(virtual_object_id = data['virtual_object_id'], object_name=data['object_name'], marker_id=data['marker_id'])
    
    # Add and commit the new object to the session
    db.session.add(new_object)
    db.session.commit()
    
    return jsonify(new_object.to_dict()), 201  # Return the created object

@app.route('/physical_configurations', methods=['POST'])
def add_physical_configuration():
    """Add a new virtual object."""
    data = request.json

    if 'physical_object_id' not in data or 'config_id' not in data or 'x_coordinate' not in data or 'y_coordinate' not in data:
        abort(400, description="Missing physical_object_id, config_id, x_coordinate or y_coordinate ")

    new_PhysicalConfiguration = PhysicalObjectConfiguration(
        physical_object_id = data['physical_object_id'],
        config_id = data['config_id'],
        x_coordinate = data['x_coordinate'],
        y_coordinate = data['y_coordinate'])
    
    # Add and commit the new object to the session
    db.session.add(new_PhysicalConfiguration)
    db.session.commit()
    
    return jsonify(new_PhysicalConfiguration.to_dict()), 201  # Return the created object

if __name__ == '__main__':
    app.run(debug=False)

