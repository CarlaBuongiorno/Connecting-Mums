import os
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
        flash(f"You have now created new event {event[event_name]}")
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

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
