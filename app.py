from flask import Flask, render_template, request, redirect, url_for,flash,session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from functools import wraps
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta


#Local Imports
from PRFSub_lib import digestFileContents, store_parsed_data, restructure_data, extract_file_details


#=============== APP CONFIG======================#
app = Flask(__name__)
app.secret_key = 'Secret123'

#Defines after how many minutes of inactivity it will tolerate before ending the session
INACTIVE_TIMEOUT = timedelta(minutes=45)

# Create a serializer
s = URLSafeTimedSerializer(app.secret_key)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://capstonepro:blowfish-orange-840@mysql.ecn.purdue.edu/capstonepro'

#MAIL INFORMATION
# Automatic Email Config for Reset Password
# Setting it to False disables Flask-SQLAlchemy's modification tracking system
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'PurdueCapstone@gmail.com'
app.config['MAIL_PASSWORD'] = 'vbla evma tqpz umof'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

#DATABASE INFORMATION
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    team_number = db.Column(db.Integer, nullable=False)

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_number = db.Column(db.Integer, nullable=False)
    team_name = db.Column(db.String(255), nullable=False)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Item_Description = db.Column(db.String(255), nullable=False)
    Part_Number = db.Column(db.String(50), nullable=True)
    Quantity = db.Column(db.Integer, nullable=True)
    Unit_Price = db.Column(db.Float, nullable=True)
    Ext_Price = db.Column(db.Float, nullable=True)
    URL_Link = db.Column(db.String(255), nullable=True)
    Delivery_Date = db.Column(db.DateTime, nullable=True)

class BOM(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_number = db.Column(db.Integer, index=True, nullable=False)
    vendor = db.Column(db.String(150), nullable=True)
    part_number = db.Column(db.String(50), nullable=True)
    item_status = db.Column(db.String(50), nullable=True)
    date = db.Column(db.DateTime, nullable=True)
    comments = db.Column(db.String(255), nullable=True)
  
class team_procurement_detail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_number = db.Column(db.Integer, index=True, nullable=False)
    item_description = db.Column(db.String(255), nullable=False)
    part_number = db.Column(db.String(50), nullable=True)
    quantity = db.Column(db.Integer, nullable=True)
    unit_price = db.Column(db.Float, nullable=True)
    ext_price = db.Column(db.Float, nullable=True)
    url_link = db.Column(db.String(255), nullable=True)
    delivery_date = db.Column(db.DateTime, nullable=True)
    file_last_modified = db.Column(db.DateTime, nullable=True)  # Last modification date of the file
    total_file_price = db.Column(db.Float, nullable=True)  # Total price from file details
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Timestamp of record creation

class approved_bom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_number = db.Column(db.Integer, index=True, nullable=False)
    item_description = db.Column(db.String(255), nullable=False)
    part_number = db.Column(db.String(50), nullable=True)
    quantity = db.Column(db.Integer, nullable=True)
    unit_price = db.Column(db.Float, nullable=True)
    ext_price = db.Column(db.Float, nullable=True)
    url_link = db.Column(db.String(255), nullable=True)
    delivery_date = db.Column(db.DateTime, nullable=True)
    file_last_modified = db.Column(db.DateTime, nullable=True)  # Last modification date of the file
    total_file_price = db.Column(db.Float, nullable=True)  # Total price from file details
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Timestamp of record creation

#FILE UPLOAD INFORMATION
UPLOAD_FOLDER = os.getcwd() + r'/uploads'
ALLOWED_EXTENSIONS = {'xlsx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#If the user is not logged in they will not be able to access certain pages
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

#Homepage
@app.route('/home')
@login_required
def home():
    # Fetch the current user's team number
    user_id = session.get('user_id')
    current_user = db.session.get(User, user_id)
    print(current_user)
    if current_user:
        team_number = current_user.team_number

    return render_template('HomePage.html', team_number=team_number)

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = INACTIVE_TIMEOUT

    if 'last_activity' in session:
        last_activity = session['last_activity']

        # Convert to offset-naive datetime if it's offset-aware
        if last_activity.tzinfo is not None and last_activity.tzinfo.utcoffset(last_activity) is not None:
            last_activity = last_activity.replace(tzinfo=None)

        now_utc = datetime.utcnow()

        if now_utc - last_activity > INACTIVE_TIMEOUT:
            session.pop('user_id', None)
            session.pop('last_activity', None)
            flash('You have been logged out due to inactivity.', 'info')
            return redirect(url_for('login'))

    session['last_activity'] = datetime.utcnow()


@app.route('/logged_out')
def logged_out():
    session.pop('user_id', None)
    return render_template('LoggedOutPage.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash('Email is required.', 'danger')
            return redirect(url_for('forgot_password'))
        
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('No account found with that email.', 'danger')
            return redirect(url_for('forgot_password'))
        
        # Sending the reset email
        msg = Message("Password Reset Request", sender="PurdueCapstone@gmail.com", recipients=[email])
        
        token = s.dumps(user.email, salt='password-reset-salt')
        reset_url = url_for('reset_password', token=token, _external=True)

        msg.body = f"Click the following link to reset your password: {reset_url}"
        mail.send(msg)
        flash('Password reset link sent to your email.', 'success')
        return redirect(url_for('login'))
    else:
        # This is the part that was missing. Return a template for the GET request.
        return render_template('ForgotPassword.html')


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600)  # Token is valid for 1 hour
    except:
        flash('The password reset link is invalid or has expired.', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not password or not confirm_password:
            flash('Both fields are required.', 'danger')
            return render_template('ResetPassword.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('ResetPassword.html')

        # Assuming you have a method to update the user's password
        user = User.query.filter_by(email=email).first()
        if user:
            user.password = password  # In the future I need to hash the password or safety
            db.session.commit()
            flash('Your password has been updated!', 'success')
            return redirect(url_for('login'))
        else:
            flash('An error occurred. Please try again.', 'danger')
            return render_template('ResetPassword.html')

    return render_template('ResetPassword.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    #print(request.form)
    if request.method == 'POST':
        #Get information from form
        email = request.form.get('email')
        password = request.form.get('password')
        
        #Checks to make sure that the user actually filled out the form
        if email and password:
            email = email.lower()
            user = User.query.filter_by(email=email).first()
        else:
            # Handle the case where email is a Nonetype (nothing populated)
            flash('Both Email and Password are required.', 'danger')
            return redirect(url_for('login'))
        
        #Validation
        print(f"Email from form: {email}")
        print(f"Password from form: {password}")

        if user and user.password == password:  # Note: This is a simple check. Hashed Password future state?
            # Log the user in (you might want to use Flask-Login for session management)
            session['user_id'] = user.id
            print("Logged in succesfully")
            return redirect(url_for('home'))  # home route
        else:
            flash('Invalid credentials. Please sign up if you do not have an account.', 'danger')
            return redirect(url_for('login'))
    
    return render_template('LoginPage.html')



@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        team_number = request.form['tnum']

        if password != confirm_password:
            # The passwords do not match, return an error message
            return "Passwords do not match", 400

        # Check if a user with the given email address already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            # A user with the given email address already exists, return an error message
            return "A user with this email address already exists", 400
        
        new_user = User(email=email, password=password, team_number=team_number)
        
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('login'))  # Redirect to the login page after successful registration
    return render_template('RegistrationPage.html')

@app.route('/add_team', methods=['POST'])
def add_team():
    team_number = request.form.get('team_number')
    team_name = request.form.get('team_name')
    team_table_name = f'team_{team_number}'

    # Create a new team-specific table if it doesn't exist
    if not db.engine.has_table(team_table_name):
        db.engine.execute(f'''
            CREATE TABLE {team_table_name} (
                id INTEGER PRIMARY KEY,
                date DATE NOT NULL,
                document VARCHAR(255) NOT NULL,
                status VARCHAR(50) NOT NULL,
                comments VARCHAR(255)
            );
        ''')

    new_team = Team(team_number=team_number, team_name=team_name)
    db.session.add(new_team)
    db.session.commit()

    return redirect(url_for('index'))

#PRFSub Endpoints
@app.route('/prfsub')
@login_required
def prfsub():
    return render_template('prfsub.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('prfsub'))
    file = request.files['file']

    # If user does not select file, browser also submits an empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('prfsub'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Fetch the current user's team number
        user_id = session.get('user_id')
        current_user = db.session.get(User, user_id)
        print(current_user)
        if current_user:
            team_number = current_user.team_number
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            flash('File successfully uploaded')
            DataInstance = digestFileContents(file_path)
            file_details = extract_file_details(DataInstance[1])
            print(file_details)
            restructured_list = restructure_data(DataInstance[1], file_details)
            print(restructured_list)
            store_parsed_data(DataInstance[1], team_number, team_procurement_detail, restructured_list, db)
            flash('File successfully uploaded')
        else:
            flash('Error: User not found.')
        return redirect(url_for('prfsub'))

    else:
        flash('Allowed file types are .xlsx')
        return redirect(url_for('prfsub'))


#Maintenence Endpoints
 #StudentBOM
@app.route('/StudentBOM', methods=['GET'])
@login_required
def studentbom():
    curr_user = session.get('user_id')
    teamquery = text("SELECT team_number FROM user WHERE id = :id LIMIT 1")
    teamres = db.session.execute(teamquery, {"id": curr_user})
    team_number = teamres.fetchone()
    
    if team_number:
        team_number_with_chars = str(team_number[0])
        # Keep only numeric characters
        teamnum = ''.join(c for c in team_number_with_chars if c.isdigit())
        
        # Query to retrieve filtered data based on the team number
        query = text("SELECT created_at, item_description, part_number, quantity, unit_price, team_number FROM team_procurement_detail WHERE team_number = :teamnum")
        result = db.session.execute(query, {"teamnum": teamnum})
        stubom_data = result.fetchall()
        
        return render_template('StudentBOM.html', stubom_data=stubom_data, teamnum=teamnum)
    
    # Handle the case where team_number is not available
    return render_template('error.html', message="Team number not found.")

@app.route('/show_users')
@login_required
def show_users():
    users = User.query.all()
    for user in users:
        print(f"ID: {user.id}, Email: {user.email}, Password: {user.password}, Team Number: {user.team_number}")
    return "Users printed in console", 200

@app.route('/')
@login_required
def root():
    return redirect(url_for('home'))


@app.route('/prf_status', methods=['GET'])
@login_required
def prfstatus():
    query = text("SELECT id, created_at, team_number FROM team_procurement_detail") 
    result = db.session.execute(query)
    prf_data = result.fetchall()
    return render_template('PrfStatus.html', prf_data=prf_data)



@app.route('/<path:unknown_route>', methods=['GET'])
def catch_all(unknown_route):
    # Redirect all unknown routes to the homepage
    return redirect(url_for('home'))

@app.route('/adminview', methods=['GET'])
@login_required
def get_user_data():
    query = text("SELECT email, team_number FROM user") 
    result = db.session.execute(query)
    user_data = result.fetchall()
    return render_template('adminview.html', user_data=user_data)

@app.route('/file_info')
@login_required
def file_info():
    # Assuming the file path is known or retrieved from the database
    file_name = 'F23_T100_PRF_Purdue.xlsx'
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
     # Check if the file exists
    if not os.path.exists(file_path):
        return {'error': 'File not found'}, 404
    last_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
    
    # Convert last_modified to a readable format
    formatted_last_modified = last_modified.strftime('%Y-%m-%d %H:%M:%S')
    
    # Return file name and last modified date as JSON
    return {
        'file_name': file_name,
        'last_modified': formatted_last_modified
    }

@app.route('/update_status', methods=['POST'])
@login_required
def update_status():
    selected_ids = request.form.getlist('selected_ids')  # Get list of selected row IDs
    
    for id in selected_ids:
        prf_row = team_procurement_detail.query.filter_by(id=id).first()  # Get the row by ID
        if prf_row:
            status = request.form.get(f'status_{id}')  # Get the selected status value for the row

            if status == 'status3':  # If status is 'Approved'
                # Move the data to the approved_bom table
                approved_data = approved_bom(
                team_number=prf_row.team_number,
                item_description=prf_row.item_description,
                part_number=prf_row.part_number,
                quantity=prf_row.quantity,
                unit_price=prf_row.unit_price,
                ext_price=prf_row.ext_price,
                url_link=prf_row.url_link,
                total_file_price=prf_row.total_file_price
                )
                db.session.add(approved_data)
                db.session.delete(prf_row)  # Delete the row from team_procurement_detail
    
    db.session.commit()
    return redirect(url_for('prfstatus'))  # Redirect to the PRF status page after processing

if __name__ == '__main__':
    app.run(debug=True)