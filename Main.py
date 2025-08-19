from flask import Flask, render_template, request, url_for, redirect, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from collections import defaultdict, OrderedDict
from datetime import datetime
import requests, re
from station_info import station_ids, line_colors
from Webscrapper import fetch_data, smart_capitalize
from datetime import date

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
    role = db.Column(db.String(50), default="user")

class Rowingdata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)  # link to Users table    password = db.Column(db.String(250), nullable=False)
    
    date = db.Column(db.Date, nullable = False, default=datetime.utcnow)
    leg_1 = db.Column(db.Float, nullable=False)
    leg_2 = db.Column(db.Float, nullable=False)
    leg_3 = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    avg_500m_time_in_secs = db.Column(db.Float, nullable = False)

    # Relationship to Users
    user = db.relationship("Users", backref=db.backref("rowing_entries", lazy=True))

    def __init__(self, user_id, leg_1, leg_2, leg_3, date=None):
        self.user_id = user_id
        self.leg_1 = leg_1
        self.leg_2 = leg_2
        self.leg_3 = leg_3
        self.total = leg_1 + leg_2 + leg_3
        
        if date:
            self.date = date

        if self.total > 0:
            self.avg_500m_time_in_secs = round((900 / self.total) * 500, 2)
        else:
            self.avg_500m_time_in_secs = 0  # fallback if distance is 0
    

def extract_platform_number(name): # extract platform number
    match = re.search(r'\d+', name)
    return int(match.group()) if match else float('inf')

def permission_required(role):
    def decorator(f):
        #@wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)  # Not logged in
            if current_user.role != role:
                abort(403)  # Forbidden
            return f(*args, **kwargs)
        return decorated_function
    return decorator

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
def tube():
    station_name = request.args.get('station', 'Acton Town')
    stop_point_ids = station_ids.get(station_name, '940GZZLUACT')  # fallback
    
    if isinstance(stop_point_ids, str):
        stop_point_ids = [stop_point_ids]

    arrivals = []

    for i, stop_point_id in enumerate(stop_point_ids):
        try:
            arrival_url = f"https://api.tfl.gov.uk/StopPoint/{stop_point_id}/Arrivals"
            response = requests.get(arrival_url)
            response.raise_for_status()
            arrivals += response.json()

            if i == 0:
                station_name_url = f"https://api.tfl.gov.uk/StopPoint/{stop_point_id}"
                station_name_response = requests.get(station_name_url)
                station_name_response.raise_for_status()
                station_name = station_name_response.json()
                station_name = station_name.get("commonName", station_name)
                station_name = station_name.replace("Underground Station", "").strip()

        except Exception as e:
                    print(f"Error: {e}")
                    station_name = "Unknown Station"
                    platforms = {}
                    fetched_time = "Unknown Time"
        
        arrivals.sort(key=lambda x: x['timeToStation']) #sort arrivals by quickest arrival
        # Time of API pull
        fetched_time = datetime.now().strftime('%H:%M:%S')

        platforms = defaultdict(list)
        seen = set() #track unique trains

        for arrival in arrivals:
            platform = arrival.get("platformName")
            if not platform:
                continue

            destination = arrival.get("destinationName")
            if not destination:
                destination = "Check front of train"
            else:
                destination = destination.replace("Underground Station", "").strip()
            if destination == station_name:
                destination = "Terminating here"
            
            line = arrival.get("lineName","").lower()
            if not line:
                continue

                # Deduplication key
            rounded_minutes = arrival.get("timeToStation", 0) // 30  # Group into 30s intervals
            key = (destination.lower(), line, rounded_minutes)
            if key in seen:
                continue
            seen.add(key)

            direction_match = re.search(r'(Northbound|Southbound|Eastbound|Westbound)', platform, re.IGNORECASE)
            direction = direction_match.group(1) if direction_match else "Unknown"

            # Extract platform number/letter
            number_match = re.search(r'Platform\s+(\w+)', platform)
            platform_number = number_match.group(1) if number_match else platform.strip()

            # Build platform label
            if direction and direction != "Unknown":
                platform_label = f"Platform {platform_number} - {direction} -"
            else:
                platform_label = f"Platform {platform_number} -"


            platforms[platform_label].append({
                "destination": destination,
                "minutes": arrival.get("timeToStation",0)//60,
                "line": line.lower()
            })

        # Sort platforms by numeric then alphabetical value
        sorted_platforms = sorted(platforms.items(), key=lambda item: (
            0 if re.match(r'Platform \d+', item[0]) else 1,               
            int(re.search(r'Platform (\d+)', item[0]).group(1)) if re.match(r'Platform \d+', item[0]) else item[0]
        ))        # numbers first, letters second
        platforms = OrderedDict(sorted_platforms)


    return render_template("tube.html",platforms=platforms, station_name=station_name,fetched_time=fetched_time,station_list=list(station_ids.keys()), line_colors=line_colors)

@app.route("/doc-who", methods =["GET","POST"])#code for the dr who page
def doc_who():
    episode_name = ''
    media_type= ''
    scraper_info = {}

    if request.method == "POST":
        episode_name = smart_capitalize(request.form.get("episode"))
        media_type = request.form.get('media_type')

        data = fetch_data(episode_name,media_type)
        if data[0] == 'N/A':
            scraper_info = {"Error": "No data found for this episode. Make sure you have spelt correctly."}
            return render_template("doc-who.html", scraper_info=scraper_info, episode_name=episode_name, media_type=media_type)
            
        else:
            season, parts, doctor, main_character, companions, featuring, enemy, writer, director = data
            
            doctor, main_character = ((doctor, []) if doctor else ([], main_character))

            # Build ordered dict with fields in desired order
            scraper_info = OrderedDict()
            scraper_info["Episode Name"] = episode_name
            scraper_info["Season"] = ", ".join(season) if season else "N/A"
            scraper_info["Number of Parts"] = parts if parts else "N/A"

            # Insert Doctor(s) or Main Character(s) here
            if doctor:
                scraper_info["Doctor(s)"] = ", ".join(doctor)
            elif main_character:
                scraper_info["Main Character(s)"] = ", ".join(main_character)

            # Continue with rest of fields
            scraper_info["Companion(s)"] = ", ".join(companions) if companions else "N/A"
            scraper_info["Featuring"] = ", ".join(featuring) if featuring else "N/A"
            scraper_info["Main Enemy"] = ", ".join(enemy) if enemy else "N/A"
            scraper_info["Writer(s)"] = ", ".join(writer) if writer else "N/A"
            scraper_info["Director(s)"] = ", ".join(director) if director else "N/A"

        return render_template("doc-who.html", scraper_info=scraper_info, episode_name=episode_name, media_type=media_type)    
    
    return render_template("doc-who.html", scraper_info=scraper_info, episode_name=episode_name, media_type=media_type)

@app.route("/rowing",  methods=["GET", "POST"] )
@permission_required("admin")
def rowing():
    leg_1 = leg_2 = leg_3 = ''
    todays_date = date.today()

    if request.method == "POST":

        leg_1 = float(request.form.get("leg_1",0))
        leg_2 = float(request.form.get("leg_2",0))
        leg_3 = float(request.form.get("leg_3",0))

        current_entry = Rowingdata(current_user.id, leg_1, leg_2, leg_3)
        db.session.add(current_entry)
        db.session.commit()

    entries = Rowingdata.query.filter_by(user_id=current_user.id).order_by(Rowingdata.date).all()

    # Prepare data for the graph
    dates = [e.date.strftime("%Y-%m-%d") for e in entries]
    avg_times = [float(e.avg_500m_time_in_secs) for e in entries]  # avg 500m time
    return render_template("rowing.html",leg_1=leg_1,leg_2=leg_2,leg_3=leg_3,date=todays_date,avg_times=avg_times,dates=dates)


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