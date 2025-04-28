import sqlite3


meetings = sqlite3.connect("meetings.db",check_same_thread=False)
c = meetings.cursor()

# Create the table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE, email TEXT UNIQUE, password TEXT NOT NULL)''')
c.execute('''CREATE TABLE IF NOT EXISTS events(event_id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT NOT NULL UNIQUE, name TEXT NOT NULL, description TEXT, creator_id INTEGER, start_date DATE NOT NULL, end_date DATE NOT NULL, time_slots_per_day INTEGER DEFAULT 360, FOREIGN KEY (creator_id) REFERENCES users(user_id))''')
c.execute('''CREATE TABLE IF NOT EXISTS availability_blocks(avail_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, weekday INTEGER NOT NULL CHECK (weekday BETWEEN 0 AND 6), time_slot INTEGER NOT NULL CHECK (time_slot BETWEEN 0 AND 360), FOREIGN KEY (user_id) REFERENCES users(user_id), UNIQUE(user_id, weekday, time_slot))''')
c.execute('''CREATE TABLE IF NOT EXISTS event_participants(participants_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, event_id INTEGER, override_availability INTEGER DEFAULT 0, FOREIGN KEY (user_id) REFERENCES users(user_id), FOREIGN KEY (event_id) REFERENCES events(event_id), UNIQUE(user_id, event_id))''')


def add_user(username, email, password):
    try:
        c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
        meetings.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # User already exists
    except Exception as e:
        print(f"Error adding user: {e}")
        return False
    
def get_user_by_username(username):
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    return c.fetchone()

def get_availability_blocks(user_id):
    c.execute("SELECT * FROM availability_blocks WHERE user_id = ?", (user_id,))
    return c.fetchall()

def get_event_by_code(code):
    c.execute("SELECT * FROM events WHERE code = ?", (code,))
    return c.fetchone()

def get_events_by_user(user_id):
    c.execute("SELECT events.event_id, events.code, events.name, events.description, events.creator_id, events.start_date, events.end_date, events.time_slots_per_day FROM events INNER JOIN event_participants ON events.event_id = event_participants.event_id WHERE event_participants.user_id = ?", (user_id,))
    return c.fetchall()