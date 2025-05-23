import flask
import databases
import datetime
app = flask.Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route("/")
def home():
    username = flask.session.get('username', '')
    return flask.render_template('index.html', username=username)

@app.route("/register", methods=["GET", "POST"])
def register():
    username = flask.session.get('username', '')
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
            flask.session['username'] = username
            flask.session.permanent = False
            return flask.redirect(flask.url_for("home_page"))
        else:
            flask.flash('User already exists or error occurred.', 'danger')
            return flask.render_template('login.html')
    return flask.render_template('login.html', username=username)

@app.route("/login", methods=["GET", "POST"])
def login():
    username = flask.session.get('username', '')
    if flask.request.method == "POST":
        username = flask.request.form["username"]
        password = flask.request.form["password"]
        
        # Call the get_user_by_username function from databases.py
        user = databases.get_user_by_username(username)
        if user and user[3] == password:
            flask.session['username'] = user[1]
            flask.session.permanent = False
            return flask.redirect(flask.url_for("home_page"))
        else:
            username = ""
            flask.flash('Invalid username or password.', 'danger')
    return flask.render_template('login.html', username=username)

@app.route("/calendar", methods=["GET", "POST"])
def home_page():
    username = flask.session.get('username', '')
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
    username = flask.session.get('username', '')
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

@app.route("/event/<code>", methods=["GET"])
def event_page(code):
    username = flask.session.get('username', '')
    joined = True
    user = databases.get_user_by_username(username)
    if user == None:
        user = ""
    if user == "":
        return flask.redirect(flask.url_for("login"))
    event = databases.get_event_by_code(code)
    if event == None:
        return "Event not found."
    user_events = databases.get_events_by_user(user[0])
    codes = [event[1] for event in user_events]
    if code not in codes:
        print(codes)
        joined = False
    participants_blocks = databases.get_event_participants_availability(event[0])
    print(joined)
    return flask.render_template('event.html', joined=joined,
                               username=username, 
                               event=event,
                               participants_blocks=participants_blocks,
                               start_date=event[5])

@app.route("/event/<code>/join", methods=["POST"])
def join_event(code):
    username = flask.session.get('username', '')
    user = databases.get_user_by_username(username)
    if user == None or user == "":
        return flask.jsonify({"error": "Not logged in"}), 401
        
    event = databases.get_event_by_code(code)
    if event == None:
        return flask.jsonify({"error": "Event not found"}), 404
        
    # Call the database function to add user to event
    if databases.add_user_to_event(user[0], event[0]):
        return flask.jsonify({"message": "Successfully joined event"}), 200
    else:
        return flask.jsonify({"error": "Error joining event"}), 500

@app.route("/your-events", methods=["GET"])
def your_events():
    username = flask.session.get('username', '')
    user = databases.get_user_by_username(username)
    if user == None:
        user = ""
    if user == "":
        return flask.redirect(flask.url_for("login"))
    events = databases.get_events_by_user(user[0])
    for i in range(len(events)):
        slots = int(events[i][8])
        start_time = events[i][7]
        if slots == 96:
            dhour = 0
            dminute = 0
        else:
            dhour = slots//4
            dminute = (slots%4)*15
        end_time = str(int(start_time.split(":")[0]) + dhour).zfill(2) + ":" + str(int(start_time.split(":")[1]) + dminute).zfill(2)
        events[i] += (end_time,)
    return flask.render_template('your-events.html', username=username, events=events)


