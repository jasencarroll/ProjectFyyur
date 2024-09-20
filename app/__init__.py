from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_moment import Moment
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost:5432/fyyur'
db = SQLAlchemy(app)
moment = Moment(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app) 

from app import routes, models, filters, forms