from flask import Flask, render_template

app = Flask(__name__)

@app.route("/") #this is the code for the base page
def home():
    return render_template("home.html")

@app.route("/weather")#this is the code for the weather page
def weather():
    return render_template("weather.html")

@app.route("/about")#this is the code for the about page
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)