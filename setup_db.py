from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://capstonepro:blowfish-orange-840@mysql.ecn.purdue.edu/capstonepro'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # To suppress a warning message

db = SQLAlchemy(app)

# Define the Items table
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Item_Description = db.Column(db.String(255), nullable=False)
    Part_Number = db.Column(db.String(50), nullable=True)
    Quantity = db.Column(db.Integer, nullable=True)
    Unit_Price = db.Column(db.Float, nullable=True)
    Ext_Price = db.Column(db.Float, nullable=True)
    URL_Link = db.Column(db.String(255), nullable=True)
    Delivery_Date = db.Column(db.DateTime, nullable=True)

# This function will create the table in the database
def create_table():
    db.create_all()

if __name__ == '__main__':
    with app.app_context():
        create_table()
