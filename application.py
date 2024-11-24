from flask import Flask, render_template, request, redirect, flash
import mysql.connector
from mysql.connector import Error
from db_config import db_config  # Import the database configuration

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a secure key for session management

# Function to establish a database connection
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=db_config["host"],
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"],
        )
        if connection.is_connected():
            print("Connected to the database")
        return connection
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM users WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            user = cursor.fetchone()
            cursor.close()
            connection.close()

            if user:
                return "Login Successful"
            else:
                flash("Invalid username or password", "error")
                return redirect("/login")
        else:
            flash("Database connection failed", "error")
            return redirect("/login")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            query = "INSERT INTO users (username, password) VALUES (%s, %s)"
            try:
                cursor.execute(query, (username, password))
                connection.commit()
                flash("Registration successful. Please log in.", "success")
                return redirect("/login")
            except Error as e:
                flash(f"Error registering user: {e}", "error")
                return redirect("/register")
            finally:
                cursor.close()
                connection.close()
        else:
            flash("Database connection failed", "error")
            return redirect("/register")

    return render_template("register.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

