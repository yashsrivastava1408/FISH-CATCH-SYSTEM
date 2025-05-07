from flask import Flask, render_template, request, redirect, session
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash  # For hashing passwords
from config import DB_CONFIG
import pickle
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # use a strong random key in production

# DB connection
connection = pymysql.connect(
    host=DB_CONFIG['host'],
    user=DB_CONFIG['user'],
    password=DB_CONFIG['password'],
    db=DB_CONFIG['database'],
    cursorclass=pymysql.cursors.DictCursor
)
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)
@app.route('/')
def home():
    return render_template('home.html')  # Updated to home.html where signup and login will be

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()

    if user and check_password_hash(user['password'], password):  # Check hashed password
        session['user_id'] = user['id']
        session['username'] = user['username']
        return redirect('/dashboard')
    else:
        return "Invalid credentials. <a href='/'>Try again</a>"

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')


        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                           (username, hashed_password, role))
            connection.commit()

        return redirect('/')  # Redirect to the home page after signup

    return render_template('signup.html')  # Serve the signup form

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM catches WHERE user_id=%s", (session['user_id'],))
        data = cursor.fetchall()

    return render_template('dashboard.html', catches=data, username=session['username'])

@app.route('/add_catch', methods=['GET', 'POST'])
def add_catch():
    if 'user_id' not in session:
        return redirect('/')

    if request.method == 'POST':
        fish_type = request.form['fish_type']
        quantity = request.form['quantity']
        catch_date = request.form['catch_date']
        latitude = request.form['latitude']
        longitude = request.form['longitude']

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO catches (user_id, fish_type, quantity, catch_date, latitude, longitude)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (session['user_id'], fish_type, quantity, catch_date, latitude, longitude))
            connection.commit()

        return redirect('/dashboard')

    return render_template('add_catch.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        # Get the date input from the form
        date_str = request.form['date']
        
        # List of possible date formats
        date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y']
        date = None

        # Try parsing with multiple formats
        for fmt in date_formats:
            try:
                date = datetime.strptime(date_str, fmt)
                break  # Exit once a valid format is found
            except ValueError:
                continue  # Continue trying the next format if one fails

        # If no valid date format is found, show an error message
        if date is None:
            return "Invalid date format. Please use one of the supported formats: YYYY-MM-DD, MM/DD/YYYY, or DD-MM-YYYY."

        # If the date is valid, continue with the prediction
        day_of_year = date.timetuple().tm_yday
        prediction = model.predict([[day_of_year]])
        predicted_quantity = round(prediction[0], 2)

        return render_template('predict.html', predicted_quantity=predicted_quantity)

    return render_template('predict.html')





if __name__ == '__main__':
    app.run(debug=True)
