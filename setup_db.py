from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://capstonepro:blowfish-orange-840@mysql.ecn.purdue.edu/capstonepro'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # To suppress a warning message

db = SQLAlchemy(app)

# Define the Items table
class BOM(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_number = db.Column(db.Integer, index=True, nullable=False)
    vendor = db.Column(db.String(150), nullable=True)
    part_number = db.Column(db.String(50), nullable=True)
    item_status = db.Column(db.String(50), nullable=True)
    date = db.Column(db.DateTime, nullable=True)
    comments = db.Column(db.String(255), nullable=True)



# This function will create the table in the database
def create_table():
    db.create_all()
    

if __name__ == '__main__':
    with app.app_context():
        create_table()
