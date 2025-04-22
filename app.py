import flask
import databases
app = flask.Flask(__name__)

username = ""

@app.route("/")
def home():
    return flask.render_template('index.html')

@app.route("/register", methods=["GET", "POST"])
def register():
    if flask.request.method == "POST":
        username = flask.request.form["username"]
        email = flask.request.form["email"]
        password = flask.request.form["password"]
        
        # Call the add_user function from databases.py
        if databases.add_user(username, email, password):
            return flask.redirect(flask.url_for("login"))
        else:
            return "User already exists or error occurred."
    return flask.render_template('register.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if flask.request.method == "POST":
        username = flask.request.form["username"]
        password = flask.request.form["password"]
        
        # Call the get_user_by_username function from databases.py
        user = databases.get_user_by_username(username)
        if user and user[3] == password:
            return flask.redirect(flask.url_for("home_page"))
        else:
            username = ""
            return "Invalid username or password."
    return flask.render_template('login.html')

@app.route("/calendar", methods=["GET", "POST"])
def home_page():
    if flask.request.method == "POST":
        # Handle form submission for creating events or other actions
        pass
    # Fetch events from the database to display on the calendar
    user = databases.get_user_by_username(username)
    availability_blocks = databases.get_availability_blocks(user[0])
    return flask.render_template('calendar.html', availability_blocks=availability_blocks)

@app.route("/create_event", methods=["GET", "POST"])
def create_event():
    if flask.request.method == "POST":
        event_name = flask.request.form["event_name"]
        event_description = flask.request.form["event_description"]
        start_date = flask.request.form["start_date"]
        end_date = flask.request.form["end_date"]
        time_slots_per_day = int(flask.request.form["time_slots_per_day"])
        
        # Call the add_event function from databases.py
        if databases.add_event(event_name, event_description, start_date, end_date, time_slots_per_day):
            return flask.redirect(flask.url_for("home_page"))
        else:
            return "Error creating event."
    return flask.render_template('create_event.html')