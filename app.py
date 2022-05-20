import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
if os.path.exists("env.py"):
    import env # nqa


# Initialize app
app = Flask(__name__)

# Config app
app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/home")
def home():
    """
        Render template for homepage
    """
    return render_template("home.html")


@app.route("/")
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
        #return redirect("get_events")
        print("pretend i blocked the user here")

    if request.method == 'POST':
        
        # request form already follows correct format for data in database,
        # so get that into dict
        event = request.form.to_dict()
        event["owner"] = session.get("event_owner", "")
        event["test_event"] = True
        #mongo.db.events.insert_one(item)
        print(event)
    else:
        print("hi")
    return render_template("events_form.html", event = [])


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
