import sqlite3
import json
import random
import string

meetings = sqlite3.connect("meetings.db",check_same_thread=False)
c = meetings.cursor()

# Create the table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE, email TEXT UNIQUE, password TEXT NOT NULL)''')
c.execute('''CREATE TABLE IF NOT EXISTS events(event_id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT NOT NULL UNIQUE, name TEXT NOT NULL, description TEXT, creator_id INTEGER, start_date DATE NOT NULL, end_date DATE NOT NULL, start_time TEXT NOT NULL, time_slots_per_day INTEGER DEFAULT 96, FOREIGN KEY (creator_id) REFERENCES users(user_id))''')
c.execute('''CREATE TABLE IF NOT EXISTS availability_blocks(avail_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, event_id INTEGER NOT NULL, availability_blocks TEXT, FOREIGN KEY (user_id) REFERENCES users(user_id), UNIQUE(user_id, event_id))''')
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
    result = c.fetchone()
    if result and result[3]:
        try:
            return json.loads(result[3]) 
        except json.JSONDecodeError:
            return []
    return []

def add_event(name, description, user_id, start_date, end_date, start_time, time_slots_per_day):
    try:
        code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        c.execute("SELECT * FROM events WHERE code = ?", (code,))
        c.fetchone()
        if c.fetchone() != None:
            return add_event(name, description, user_id, start_date, end_date, start_time, time_slots_per_day)
        else:
            c.execute("INSERT INTO events (code, name, creator_id, description, start_date, end_date, start_time, time_slots_per_day) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (code, name, user_id, description, start_date, end_date, start_time, time_slots_per_day))
            meetings.commit()
            return code
    except sqlite3.IntegrityError:
        return False  # Event already exists
    except Exception as e:
        print(f"Error adding event: {e}")
        return False

def get_event_by_code(code):
    c.execute("SELECT * FROM events WHERE code = ?", (code,))
    return c.fetchone()

def get_events_by_user(user_id):
    c.execute("SELECT events.event_id, events.code, events.name, events.description, events.creator_id, events.start_date, events.end_date, events.start_time, events.time_slots_per_day, users.username FROM events INNER JOIN event_participants ON events.event_id = event_participants.event_id INNER JOIN users ON events.creator_id = users.user_id WHERE event_participants.user_id = ?", (user_id,))
    return c.fetchall()

# Account calendar is event_id 0
def update_availability_blocks(user_id, event_id, availability_blocks):
    try:
        blocks_json = json.dumps(availability_blocks)
        c.execute("INSERT OR REPLACE INTO availability_blocks (user_id, event_id, availability_blocks) VALUES (?, ?, ?)", (user_id, event_id, blocks_json))
        meetings.commit()
        return True
    except Exception as e:
        print(f"Error updating availability blocks: {e}")
        return False
    
def add_user_to_event(user_id, event_id, override_availability=0):
    try:
        c.execute("INSERT OR REPLACE INTO event_participants (user_id, event_id, override_availability) VALUES (?, ?, ?)", (user_id, event_id, override_availability))
        meetings.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # User already exists in the event
    except Exception as e:
        print(f"Error adding user to event: {e}")
        return False
    
def get_event_participants_availability(event_id):
    try:
        c.execute("""SELECT users.username, availability_blocks.availability_blocks FROM availability_blocks INNER JOIN event_participants ON event_participants.user_id = availability_blocks.user_id INNER JOIN users ON availability_blocks.user_id = users.user_id WHERE event_participants.event_id = ?""", (event_id, ))
        
        results = c.fetchall()
        availability_map = {}
        
        for result in results:
            username = result[0]
            blocks = json.loads(result[1]) if result[1] else []
            availability_map[username] = blocks
        return availability_map
    except Exception as e:
        print(f"Error getting participants availability: {e}")
        return {}