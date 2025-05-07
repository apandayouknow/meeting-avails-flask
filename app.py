import flask
import databases
import datetime
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
    user = databases.get_user_by_username(username)
    if flask.request.method == "POST":
        data = flask.request.json
        blocks = data.get("blocks",[])
        success = databases.update_availability_blocks(user[0], 0, blocks)

    # Fetch events from the database to display on the calendar
    if user == None:
        user = ""
    if user == "":
        return flask.redirect(flask.url_for("login"))
    availability_blocks = databases.get_availability_blocks(user[0])
    if availability_blocks == None:
        availability_blocks = []
    #today's date
    today = datetime.datetime.today().strftime('%m-%d-%Y')
    print(today)
    return flask.render_template('calendar.html', start_date=today, username=username, availability_blocks=availability_blocks)

@app.route("/new-event", methods=["GET", "POST"])
def new_event():
    global username
    user = databases.get_user_by_username(username)
    if user == None:
        user = ""
    if user == "":
        return flask.redirect(flask.url_for("login"))
    
    if flask.request.method == "POST":
        event_name = flask.request.form["name"]
        event_description = flask.request.form["description"]
        start_date = flask.request.form["start_date"]
        end_date = flask.request.form["end_date"]
        start_time = flask.request.form["start_time"]
        time_slots_per_day = int(flask.request.form["time_slots_per_day"])
        
        # Call the add_event function from databases.py
        code = databases.add_event(event_name, event_description, user[0], start_date, end_date, start_time, time_slots_per_day)
        if code != False:
            return flask.redirect(flask.url_for("event_page", code=code))
        else:
            return "Error creating event."
    return flask.render_template('new-event.html', username=username)

@app.route("/event/<code>", methods=["GET", "POST"])
def event_page(code):
    global username
    user = databases.get_user_by_username(username)
    if user == None:
        user = ""
    if user == "":
        return flask.redirect(flask.url_for("login"))
    event = databases.get_event_by_code(code)
    if event == None:
        return "Event not found."
    if code not in databases.get_events_by_user(user[0]):
        databases.add_user_to_event(user[0], event[0])
    participants_blocks = databases.get_event_participants_availability(event[0])
    
    return flask.render_template('event.html', 
                               username=username, 
                               event=event,
                               participants_blocks=participants_blocks,
                               start_date=event[5])  # event start_date
