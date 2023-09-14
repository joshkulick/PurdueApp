from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('HomePage.html')

@app.route('/logged_out')
def logged_out():
    return render_template('LoggedOutPage.html')

@app.route('/login')
def login():
    return render_template('LoginPage.html')

@app.route('/prf_status')
def prf_status():
    return render_template('PrfStatus.html')

@app.route('/registration')
def registration():
    return render_template('RegistrationPage.html')

@app.route('/start_here')
def start_here():
    return render_template('StartHere.html')

@app.route('/prfsub')
def prfsub():
    return render_template('prfsub.html')

if __name__ == '__main__':
    app.run(debug=True)
