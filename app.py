import flask
import databases
app = flask.Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

username = ""

@app.route("/")
def home():
    return flask.render_template('index.html', username=username)

@app.route("/register", methods=["GET", "POST"])
def register():
    if flask.request.method == "POST":
        username = flask.request.form["username"]
        email = flask.request.form["email"]
        password = flask.request.form["password"]
        confirm_password = flask.request.form['confirm_password']

        if password != confirm_password:
            flask.flash('Passwords do not match!', 'danger')
            return flask.render_template('login.html')
        
        # Call the add_user function from databases.py
        if databases.add_user(username, email, password):
            return flask.redirect(flask.url_for("login"))
        else:
            flask.flash('User already exists or error occurred.', 'danger')
            return flask.render_template('login.html')
    return flask.render_template('login.html', username=username)

@app.route("/login", methods=["GET", "POST"])
def login():
    global username
    if flask.request.method == "POST":
        username = flask.request.form["username"]
        password = flask.request.form["password"]
        
        # Call the get_user_by_username function from databases.py
        user = databases.get_user_by_username(username)
        if user and user[3] == password:
            return flask.redirect(flask.url_for("home_page"))
        else:
            username = ""
            flask.flash('Invalid username or password.', 'danger')
    return flask.render_template('login.html', username=username)

@app.route("/calendar", methods=["GET", "POST"])
def home_page():
    global username
    if flask.request.method == "POST":
        # Handle form submission for creating events or other actions
        pass
    # Fetch events from the database to display on the calendar
    user = databases.get_user_by_username(username)
    if user == None:
        user = ""
    if user == "":
        return flask.redirect(flask.url_for("login"))
    availability_blocks = databases.get_availability_blocks(user[0])
    if availability_blocks == None:
        availability_blocks = []
    return flask.render_template('calendar.html', username=username, availability_blocks=availability_blocks)

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
            return flask.redirect(flask.url_for("home_page"),username=username)
        else:
            return "Error creating event."
    return flask.render_template('create_event.html', username=username)