from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://capstonepro:blowfish-orange-840@mysql.ecn.purdue.edu/capstonepro'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # To suppress a warning message

db = SQLAlchemy(app)

# Define the Items table
class TeamProcurementDetail(db.Model):
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

# This function will create the table in the database
def create_table():
    db.create_all()

if __name__ == '__main__':
    with app.app_context():
        create_table()
