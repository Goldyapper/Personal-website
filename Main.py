from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from collections import defaultdict, OrderedDict
from datetime import datetime
import requests, re
from station_ids import station_ids

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
    station_name = request.args.get('station', 'Acton Town')
    stop_point_id = station_ids.get(station_name, '940GZZLUACT')  # fallback
    arrival_url = f"https://api.tfl.gov.uk/StopPoint/{stop_point_id}/Arrivals"
    station_name_url = f"https://api.tfl.gov.uk/StopPoint/{stop_point_id}"

    try:

        station_name_response = requests.get(station_name_url)
        station_name_response.raise_for_status()
        station_name = station_name_response.json()
        station_name = station_name.get("commonName", "Unknown Station")
        station_name = station_name.replace("Underground Station", "").strip()


        #arrival data pulling
        arrival_response = requests.get(arrival_url) #get website
        arrival_response.raise_for_status() 
        arrivals = arrival_response.json()
        arrivals.sort(key=lambda x: x['timeToStation']) #sort arrivals by quickest arrival

        # Time of API pull
        fetched_time = datetime.now().strftime('%H:%M:%S')

        platforms = defaultdict(list)

        for arrival in arrivals:
            platform = arrival.get("platformName")
            if not platform or "platform" not in platform.lower():
                continue

            destination = arrival.get("destinationName")

            if not destination:
                destination = "Check front of train"
            else:
                destination = destination.replace("Underground Station", "").strip()

            if destination == station_name:
                destination = "Terminating here"
            

            line = arrival.get("lineName","")
            if not line:
                continue

            direction_match = re.search(r'(Northbound|Southbound|Eastbound|Westbound)', platform, re.IGNORECASE)
            if not direction_match:
                continue

            direction = direction_match.group(1) 
            if not direction_match:
                continue

            platform_label = f"{platform.split('-')[1].strip()} - {direction.capitalize()} - {line} Line"

            platforms[platform_label].append({
                "destination": destination,
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
        station_name = "Unknown Station"
        platforms = {}
        fetched_time = "Unknown Time"

    return render_template("tube.html",platforms=platforms, station_name=station_name,fetched_time=fetched_time,station_list=list(station_ids.keys()))

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