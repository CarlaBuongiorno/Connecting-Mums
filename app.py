import os
import datetime
import re
from functools import wraps
import dateutil.parser
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env  # nqa


# Initialize app
app = Flask(__name__)

# Config app
app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


def login_required(f):
    """
        Page is only accessed if user is logged in
        @login_required decorator
        https://flask.palletsprojects.com/en/2.0.x/patterns/viewdecorators/#login-required-decorator
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # no "user" in session
        if "user" not in session:
            flash("You must log in to view this page", "danger")
            return redirect(url_for("login"))
        # user is in session
        return f(*args, **kwargs)
    return decorated_function


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
            "email": request.form.get("email"),
            "my_journal": [],
            "created_events": []
        }
        mongo.db.users.insert_one(register_user)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!", "success")
        return redirect(url_for("profile", username=session["user"]))

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


@app.route("/get_events", methods=["GET", "POST"])
def get_events():
    """
        Get all events in the database to
        display on 'Events' page.
    """
    if request.method == "POST":
        # allows text search to happen, might just need to be
        # moved to when items are added?
        mongo.db.events.create_index(
            [
                ("event_name", "text"),
                ("event_description", "text"),
                ("event_place", "text"),
            ])
        events = mongo.db.events.find(
            {"$text": {"$search": request.form["query"]}})
    else:
        events = mongo.db.events.find()

    events = events.sort("event_date")

    # allows page to know if an event is in the past, and change display if so
    now = datetime.datetime.now()
    return render_template("events.html", events=events, now=now)


@app.route("/new_event", methods=["GET", "POST"])
@login_required
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
        event["event_date"] = dateutil.parser.parse(event["event_date"])

        mongo.db.events.insert_one(event)
        flash(f"You have now created new event {event['event_name']}")
        return redirect("/get_events")
    return render_template("events_form.html")


@app.route("/attend_event/<event_id>")
@login_required
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
            {"members_attending": session.get("user", "")}}
        )
    return redirect("/get_events")


@app.template_filter('format_date')
def formate_date(value, format="%d/%m/%y at %H:%M"):
    return value.strftime(format)


@app.route("/new_gratitude", methods=["GET", "POST"])
@login_required
def new_gratitude():
    '''
    Create a new gratitude in user journal / profile
    '''
    username = mongo.db.username.find_one(
        {"username": session["user"].lower()})

    if session.get("user", "") == "":  # only allow add if admin
        flash("Please log in before creating a new gratitude to your journal")
        return redirect("/login")

    if request.method == 'POST':
        # get gratitudes from journal
        journal_entry = {
            "gratitude_date": request.form.get("gratitude_date"),
            "gratitude_1": request.form.get("gratitude_1"),
            "gratitude_2": request.form.get("gratitude_2"),
            "gratitude_3": request.form.get("gratitude_3"),
        }

        journal = mongo.db.my_journal.insert_one(journal_entry).limit(3)
        _id = journal.inserted_id
        mongo.db.username.update_one(
            {"username": session["user"]},{"$push": {"my_journal": _id}})
        flash("You added gratitudes to your journal today, well done!")
        return redirect("/profile/<username>")
    return render_template(
        "profile.html", username=username, journal_entry=journal_entry)


@app.route("/profile/<username>", methods=["GET", "POST"])
@login_required
def profile(username):
    """
        Get username from db. Render profile page. Find user's attending
        events and created events to display on profile page..
    """
    # grab the session user's username from the db
    username = mongo.db.users.find_one(
            {"username": session["user"]})["username"]
    events = mongo.db.events.find()
    my_journal = mongo.db.my_journal.find()

    return render_template(
        "profile.html", username=username, events=list(events), my_journal=my_journal)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
