import os
import re
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env # nqa


# Initialize app
app = Flask(__name__)

# Config app
app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/home")
def home():
    """
        Render template for homepage
    """
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """
        Get user's username from the form, check if it already exists in
        the database. If it does, flash a message to the user and redirect to
        registration page. Save user in the database, put user into a session
        cookie and redirect to profile page.
    """
    if request.method == "POST":

        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": "username"})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        # check if passwords match
        password = request.form.get("password")
        confirm_password = request.form.get("confirm-password")

        if password != confirm_password:
            flash("Your passwords don't match", "danger")
            return redirect(url_for("register"))

        # check if password conforms to pattern
        is_digit = re.compile(r"[0-9]")
        is_lower = re.compile(r"[a-z]")
        is_upper = re.compile(r"[A-Z]")

        if is_digit.search(password) is None or \
            is_lower.search(password) is None or \
                is_upper.search(password) is None:
            return redirect(url_for("register"))

        register_user = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "email": request.form.get("email")
        }
        mongo.db.users.insert_one(register_user)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!", "success")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """
        Find username in db, check that user's password matches what's in
        the db, render login page if no match, render profile page if match.
    """
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(
                    request.form.get("username")), "success")
                return redirect(url_for(
                    "profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password", "danger")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    """
    Remove user from session cookies. Render login page.
    """
    flash("You have been logged out", "success")
    session.pop("user")
    return redirect(url_for("home"))


@app.route("/get_events")
def get_events():
    """
        Get all events in the database to
        display on 'Events' page.
    """
    events = mongo.db.events.find()
    return render_template("events.html", events=events)


@app.route("/new_event", methods=["GET", "POST"])
def new_event():
    '''
    Create a new event by the user
    '''
    if session.get("user", "") == "":  # only allow add if admin
        flash("Please log in before creating a new event")
        return redirect("get_events")

    if request.method == 'POST':

        # request form already follows correct format for data in database,
        # so get that into dict
        event = request.form.to_dict()
        event["event_owner"] = session.get("user", "")
        event["members_attending"] = []
        event["test_event"] = True
        mongo.db.events.insert_one(event)
        flash(f"You have now created new event {event['event_name']}")
        return redirect("/get_events")
    return render_template("events_form.html")


@app.route("/attend_event/<event_id>")
def attend_event(event_id):
    '''
    Allows a user to say they want to attend a given event
    '''
    if session.get("user", "") == "":
        flash("please log in so we can know whos going")
        return redirect("/get_events")
    
    mongo.db.events.update_one(
        {"_id": ObjectId(event_id)},
        {"$addToSet": 
            {"members_attending": session.get("user", "")}
        })
    return redirect("/get_events")


@app.template_filter('format_date')
def formate_date(value):
    if not value:
        return "date not set"
    dateTime = getDate(value)
    date = dateTime["date"]
    time = dateTime["time"]
    return f"{date[2]}/{date[1]}/{date[0]} at {time}"

def getDate(dateString):
    dateTime = dateString.split("T")
    return {"date": dateTime[0].split("-"), "time": dateTime[1]}

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
