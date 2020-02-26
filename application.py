from flask import Flask, request, jsonify, abort, session, render_template, redirect, url_for, flash
from flask_user import roles_required
from flask_login import LoginManager
from app_models import *
import requests

app = Flask("FuelTrackingSystem")
login = LoginManager(app)
app.config['SESSION_TYPE'] = 'memcache'
app.secret_key = "super secret key"

@login.user_loader 
def load_user(id): 
        return User.get(int(id)) 

db.create_tables([User, FuelInfo, VehicleInfo])
#u=User(username="admin", password="admin", role="admin", email_address="d@gmail.com",vehicle_number="123", phone_number="sads")
#u.save()

@app.route("/test")
@auth.login_required
@permission_required("admin")
def register_test():
    return "Hello, World!"

@app.route('/register_backup', methods = ['POST'])
@auth.login_required
@permission_required("admin")
def add_new_user_backup():
    username = request.json.get('username')
    password = request.json.get('password')
    email_address = request.json.get('email_address')
    phone_number = request.json.get('phone_number')
    vehicle_number = request.json.get('vehicle_number')
    role = request.json.get("role")
    if User.get_or_none(User.username == username) is not None:
        flash('Please check your login details and try again.')
        return redirect(url_for('register')) 
    user = User(username = username,password=password,role=role, email_address=email_address, vehicle_number=vehicle_number, phone_number=phone_number)
    user.save()
    return jsonify({ 'username': user.username }), 201 #{'Location': url_for('get_user', id = user.id, _external = True)}



@app.route('/adddata/vehicle', methods = ['POST'])
@auth.login_required
@permission_required("user")
def add_vehicle_info():
    username = current_user.username
    user = User.get_or_none(User.username==username)
    #import pdb;pdb.set_trace()
    if user:
        print("Request from add vehicle data: " + str(request.json))
        latitude=request.json.get("latitude")
        longitude=request.json.get("longitude")
        VehicleInfo.create(user=user,latitude=latitude,longitude=longitude)
        #vehicle_info.save()
        return jsonify({ 'message': "Data saved successfully" }), 201 
    return jsonify({ 'message': "Error" }), 500 


@app.route('/adddata/fuel', methods = ['POST'])
@auth.login_required
@permission_required("user")
def add_fuel_info():
    username = current_user.username
    user = User.get_or_none(User.username==username)
    if user:
        print("Request from add fuel data: " + str(request.json))
        quantity=request.json.get("quantity")
        fuel_info = FuelInfo(user = user,quantity=quantity)
        fuel_info.save()
        return jsonify({ 'message': "Data saved successfully" }), 201
    return jsonify({ 'message': "Error" }), 500





@app.route('/register')
@permission_required("admin")
@login_required
def register():
    return render_template('register.html')


@app.route('/viewvehicleinfo')
@login_required
@permission_required("user")
def view_vehicle_info():
    username = current_user.username
    user = User.get_or_none(User.username==username)
    data=[]
    if user:
        vehicle_info=VehicleInfo.select().where(VehicleInfo.user==user).order_by(VehicleInfo.created_at.desc())
        for v in vehicle_info:
            d={"date": v.created_at, "latitude": v.latitude, "longitude": v.longitude}
            data.append(d)
    return render_template('vehicle_info.html', data=data, vehicle_number=user.vehicle_number)

@app.route('/viewvehicleinforaw')
@login_required
@permission_required("user")
def view_vehicle_info_raw():
    username = current_user.username
    user = User.get_or_none(User.username==username)
    data=[]
    if user:
        vehicle_info=VehicleInfo.select().where(VehicleInfo.user==user).order_by(VehicleInfo.created_at.desc())
        for v in vehicle_info:
            d={"date": v.created_at, "latitude": v.latitude, "longitude": v.longitude}
            data.append(d)
    return render_template('vehicle_info_raw.html', data=data, vehicle_number=user.vehicle_number)

@app.route('/viewfuelinfo')
@login_required
@permission_required("user")
def view_fuel_info():
    username = current_user.username
    user = User.get_or_none(User.username==username)
    data=[]
    if user:
        fuel_info=FuelInfo.select().where(FuelInfo.user==user).order_by(FuelInfo.created_at.desc())
        for v in fuel_info:
            d={"date": v.created_at, "quantity": v.quantity}
            data.append(d)
    return render_template('fuel_info.html', data=data, vehicle_number=user.vehicle_number)

@app.route('/register', methods = ['POST'])
@login_required
@permission_required("admin")
def add_new_user():
    username = request.form.get('username')
    password = request.form.get('password')
    email_address = request.form.get('email_address')
    phone_number = request.form.get('phone_number')
    vehicle_number = request.form.get('vehicle_number')
    role = request.form.get("role")
    if username is None or password is None or role is None:
        flash('Some of the provided fields are null')
    if User.get_or_none(User.username == username) is not None:
        flash('User with same username already exist.')
        return redirect(url_for('register')) 
    user = User(username = username,password=password,role=role, email_address=email_address, vehicle_number=vehicle_number, phone_number=phone_number)
    user.save()
    flash('User registered successfully')
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    user=User.get_or_none((User.username == username) & (User.password == password))
    if user:
        login_user(user, remember=remember)
        return redirect(url_for('profile'))
    else:
        flash('Please check your login details and try again.')
        return redirect(url_for('login'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.config['SESSION_TYPE'] = 'memcache'
    app.secret_key = "super secret key"
    #u=User(username="sachin", password="sachin", role="admin", email_address="d@gmail.com",vehicle_number="123", phone_number="sads")
    #u.save()
    #u=User(username="sachin", password="sachin", role="admin", email_address="d@gmail.com",vehicle_number="123", phone_number="sads")
    #u.save()
    
    app.run(host='0.0.0.0', port=5000, debug=True)
