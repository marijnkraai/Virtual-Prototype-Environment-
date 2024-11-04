from db_config import DATABASE_URL, WS_SECRETKEY
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SECRET_KEY'] = WS_SECRETKEY 
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_size": 10,          # Number of connections to keep in the pool
    "max_overflow": 20,       # Maximum number of additional connections beyond pool_size
    "pool_timeout": 30,       # Maximum time to wait for a connection in seconds
    "pool_recycle": 1800      # Recycle connections after 1800 seconds to avoid stale connections
}