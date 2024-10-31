from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import pickle
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = '123456'  # Set a secret key for sessions

# MySQL Database configuration
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",  # Replace with your MySQL username
    password="password",  # Replace with your MySQL password
    database="loan_eligibility"  # Replace with your database name
)

cursor = db_connection.cursor()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        
        # Insert user data into database
        cursor.execute("INSERT INTO User (username, password) VALUES (%s, %s)", (username, password))
        db_connection.commit()
        
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor.execute("SELECT password FROM User WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user[0], password):
            session['username'] = username
            return redirect(url_for('predict'))
        else:
            return "Invalid credentials. Please try again."
    
    return render_template('login.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'username' in session:
        if request.method == 'POST':
            # Capture form data for loan prediction
            gender = request.form['gender']
            marital_status = request.form['marital_status']
            education = request.form['education']
            dependents = request.form['dependents']
            income = float(request.form['income'])
            co_income = float(request.form['co_income'])
            loan_amount = float(request.form['loan_amount'])
            loan_term = float(request.form['loan_term'])
            credit_history = int(request.form['credit_history'])
            property_area = request.form['property_area']
            
            # Load the pre-trained model
            with open('model.pkl', 'rb') as model_file:
                model = pickle.load(model_file)
            
            # Prepare data for prediction
            input_data = [[gender, marital_status, education, dependents, income, co_income, loan_amount, loan_term, credit_history, property_area]]
            
            # Make prediction
            prediction = model.predict(input_data)
            result = 'Eligible for Loan' if prediction == 1 else 'Not Eligible for Loan'
            
            return render_template('result.html', prediction=result)
        
        return render_template('predict.html')
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)
