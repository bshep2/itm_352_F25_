from flask import Flask, render_template, request, redirect, url_for


app = Flask(__name__)


# Hardcoded user data (usernames and passwords)
users = {
   "user1": "password1",
   "user2": "password2"
}


# Route for the home page
@app.route('/')
def home():
   return render_template('index.html')


# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
   if request.method == 'POST':
       # Get the username and password from the form
       username = request.form['username']
       password = request.form['password']
      
       # Check if the username and password match any entry in the 'users' dictionary
       if username in users and users[username] == password:
           return redirect(url_for('success'))  # Redirect to success page if login is successful
       else:
           return "Invalid username or password, please try again."


   return render_template('login.html')


# Route for the success page after login
@app.route('/success')
def success():
   return render_template('success.html')


# Run the application
if __name__ == "__main__":
   app.run(debug=True)
