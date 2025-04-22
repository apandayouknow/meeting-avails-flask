-- Main users database
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT UNIQUE,
    password_hash TEXT NOT NULL,
);

-- Time blocks when users are not available
CREATE TABLE availability_blocks (
    avail_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    weekday INTEGER NOT NULL CHECK (weekday BETWEEN 0 AND 6), -- 0 = Monday
    time_slot INTEGER NOT NULL CHECK (time_slot BETWEEN 0 AND 96), -- 24 hours of 15 minute slots
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id, weekday, time_slot)
);

-- Events database with creator and event data
CREATE TABLE events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE, -- 6-char access code
    name TEXT NOT NULL,
    description TEXT,
    creator_id INTEGER,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    time_slots_per_day INTEGER DEFAULT 96, -- 24 hours of 15 minute slots
    FOREIGN KEY (creator_id) REFERENCES users(id)
);

-- Table with all the participants in each event
CREATE TABLE event_participants (
    partcipants_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    event_id INTEGER,
    override_availability INTEGER DEFAULT 0, -- 1 if user customizes availability
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (event_id) REFERENCES events(event_id),
    UNIQUE(user_id, event_id)
);

/*
-- Separate availabilities table to track user availability
CREATE TABLE availabilities (
    avail_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    event_id INTEGER,
    date DATE NOT NULL,
    time_slot INTEGER NOT NULL,
    available INTEGER NOT NULL CHECK (available IN (0, 1)),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (event_id) REFERENCES events(id),
    UNIQUE(user_id, event_id, date, time_slot)
);
*/
