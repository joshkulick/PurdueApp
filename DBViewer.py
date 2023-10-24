from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect,text

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://capstonepro:blowfish-orange-840@mysql.ecn.purdue.edu/capstonepro'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # To suppress a warning message

db = SQLAlchemy(app)

@app.route('/tables', methods=['GET'])
def list_tables():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    return jsonify(tables)

@app.route('/table/<table_name>', methods=['GET'])
def view_table(table_name):
    # WARNING: This approach of directly embedding the table name in SQL is not safe from SQL injection.
    # Use ORM or safer methods for production purposes.
    query = text(f'SELECT * FROM {table_name}')
    result = db.session.execute(query)
    columns = result.keys()
    rows = result.fetchall()
    data = [dict(zip(columns, row)) for row in rows]
    return jsonify(data)

if __name__ == '__main__':
    menu = """
    Choose an option:
    1. List tables
    2. View table content
    3. Exit
    """
    while True:
        print(menu)
        choice = input("Enter your choice: ")
        if choice == '1':
            with app.test_request_context():
                response = list_tables()
                print(response.get_json())
        elif choice == '2':
            table_name = input("Enter table name: ")
            with app.test_request_context():
                response = view_table(table_name)
                for record in response.get_json():
                    print(record)
        elif choice == '3':
            break
        else:
            print("Invalid choice.")
