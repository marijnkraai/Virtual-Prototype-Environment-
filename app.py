

from db_config import DATABASE_URL
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
from models import Base, PhysicalObject  # Import the common model

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create a db instance
db = SQLAlchemy(app)

# Initialize the app context for Flask-SQLAlchemy
with app.app_context():
    db.create_all()  # Create tables if they don't exist

@app.route('/physical_objects', methods=['GET'])
def get_physical_objects():
    """Retrieve all physical objects."""
    stmt = select(PhysicalObject)  # Create a select statement for the model
    result = db.session.execute(stmt)  # Execute the statement
    objects = result.scalars().all()  # Get the results as a list of instances
    return jsonify([obj.to_dict() for obj in objects])  # Convert to dict for JSON

@app.route('/physical_objects', methods=['POST'])
def add_physical_object():
    """Add a new physical object."""
    data = request.json
    new_object = PhysicalObject(object_name=data['object_name'], marker_id=data['marker_id'])
    
    # Add and commit the new object to the session
    db.session.add(new_object)
    db.session.commit()
    
    return jsonify(new_object.to_dict()), 201  # Return the created object

if __name__ == '__main__':
    app.run(debug=True)

