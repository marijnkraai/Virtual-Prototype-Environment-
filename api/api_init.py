from db_config import DATABASE_URL, WS_SECRETKEY
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SECRET_KEY'] = WS_SECRETKEY 