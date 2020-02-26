from peewee import *
import datetime
from flask_login import UserMixin, current_user, login_user, logout_user, login_required
#from application import login
from flask_httpauth import HTTPBasicAuth
from functools import wraps
from flask import g
from flask import abort, flash, session, render_template, redirect, url_for

auth = HTTPBasicAuth()

db = SqliteDatabase('fueltracking.db', pragmas={
    'journal_mode': 'wal',
    'cache_size': -1024 * 64})

# Connect to a MySQL database on network.
#db = MySQLDatabase('fueltracking', user='root', password='root',
#                         host='localhost', port=3316)

class BaseModel(Model):
    class Meta:
        database = db

# the user model specifies its fields (or columns) declaratively, like django
class User(UserMixin, BaseModel):
    __tablename__ = 'users'

    username = TextField()
    password = TextField()
    created_at = DateTimeField(default=datetime.datetime.now)
    phone_number = TextField()
    role=TextField()
    email_address=TextField()
    vehicle_number=TextField()


class FuelInfo(BaseModel):
    __tablename__ = 'fuel_info'
    created_at = DateTimeField(default=datetime.datetime.now)
    quantity = TextField()
    user = ForeignKeyField(User)

class VehicleInfo(BaseModel):
    __tablename__ = 'vehicle_info'
   
    created_at = DateTimeField(default=datetime.datetime.now)
    latitude = TextField()
    longitude = TextField()
    user = ForeignKeyField(User)

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            #import pdb;pdb.set_trace()
            if not current_user.role == permission:
                logout_user()
                #abort(403)
                flash('Please check your login details and permission to access this page and try again.')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth.verify_password
def verify_password(username, password):
    user = User.get_or_none((User.username == username) & (User.password==password))
    if not user:
        return False
    g.user = user
    login_user(user)
    return True
