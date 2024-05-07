from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
import os
from werkzeug.utils import secure_filename
import base64

app = Flask(__name__)
app.secret_key = '2e69e3cf3e2ae34c7b2a4718268a1ea7'  # Replace this with your actual secret key

# MongoDB connection string
# Replace <password> with your actual password
# client = MongoClient("mongodb+srv://user1:12345@atlascluster.nq1qhdg.mongodb.net/")
client = MongoClient("mongodb://localhost:27017")
# Select the database to use
db = client["lunge"]

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = db.users.find_one({'email': email, 'password': password})
        if user:
            session['email'] = email  # Store the email in the session
            return redirect(url_for('profile', message='Signin successful!'))
        else:
            return redirect(url_for('signin', message='Invalid email or password. Please try again.'))

    # Get the message from the query parameters
    message = request.args.get('message', None)
    return render_template('signin.html', message=message)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Extract name, email, and password from the form
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Check if email already exists in the database
        existing_user = db.users.find_one({'email': email})
        if existing_user:
            # Email already exists, return a message to the user
            return render_template('signup.html', message="Email already exists! Try again with a different email.")

        # Insert new user into the database
        db.users.insert_one({'name': name, 'email': email, 'password': password})
        # Signup successful, redirect to the sign-in page
        return redirect(url_for('signin', message='Signup successful!'))

    return render_template('signup.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    # Check if the user is logged in
    if 'email' in session:
        # Get the email of the logged-in user from the session
        email = session['email']
        
        # Query the database to fetch user data
        user = db.users.find_one({'email': email})

        # Check if user data exists
        if user:
            message = request.args.get('message', None)
            # User data exists, pass it to the template
            return render_template('profile.html', user=user, message=message)
    
    # Redirect to the sign-in page if the user is not logged in
    return redirect(url_for('signin'))

@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    if request.method == 'POST':
        # Get the email of the logged-in user from the session
        email = session['email']
        
        # Get the form data
        name = request.form['name']
        address = request.form['address']
        profile_image = request.files['profile_image']
        
        # Convert the image file to base64 encoding
        if profile_image:
            profile_image_data = base64.b64encode(profile_image.read()).decode('utf-8')
        else:
            profile_image_data = None
        
        # Update user data in the database
        db.users.update_one({'email': email}, {'$set': {'name': name, 'address': address, 'profile_image': profile_image_data}})
        
        # Redirect to the profile page with a success message
        return redirect(url_for('profile', message='Profile updated successfully!'))

    # Render the update profile page
    return render_template('update_profile.html')

@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    # Redirect to the sign-in page
    return redirect(url_for('signin'))
@app.route('/doctors', methods=['GET'])
def doctors():
    return render_template('doc.html')


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
