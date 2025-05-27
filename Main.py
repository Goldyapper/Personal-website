from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from collections import defaultdict, OrderedDict
import requests, re

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SECRET_KEY"] = "supersecretkey"

# Initialize database and login manager
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# User model
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)

def extract_platform_number(name): # extract platform number
    match = re.search(r'\d+', name)
    return int(match.group()) if match else float('inf')

# Create database
with app.app_context():
    db.create_all()

# Wembley Park StopPoint ID (TfL internal ID for the station)
STOPPOINT_ID = "940GZZLUWYP"

# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route("/") #this is the code for the base page
def home():
    return render_template("home.html")

@app.route("/weather")#this is the code for the weather page
def weather():
    return render_template("weather.html")

@app.route("/tube")
def tube_departure():
    url = f"https://api.tfl.gov.uk/StopPoint/{STOPPOINT_ID}/Arrivals"

    try:
        response = requests.get(url) #get website
        response.raise_for_status() 

        arrivals = response.json()
        arrivals.sort(key=lambda x: x['timeToStation']) #sort arrivals by quickest arrival

        platforms = defaultdict(list)
        for arrival in arrivals:
            platforms[arrival.get('platformName', 'Unknown')].append({
                "line": arrival.get("lineName"),
                "destination": arrival.get("destinationName"),
                "minutes": arrival.get("timeToStation",0)//60
            })

        # Sort platforms by numeric value
        sorted_platforms = sorted(
            platforms.items(),
            key=lambda item: extract_platform_number(item[0])
        )

        platforms = OrderedDict(sorted_platforms)



    except Exception as e:
        print(f"Error: {e}")
        platforms = {}

    return render_template("tube.html",platforms=platforms)

@app.route("/about")#this is the code for the about page
def about():
    return render_template("about.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if Users.query.filter_by(username=username).first():
            return render_template("register.html", error="Username already taken!")

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

        new_user = Users(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))
    
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = Users.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)