CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    name TEXT NOT_NULL
    );

CREATE TABLE matches (
    match_id INTEGER PRIMARY KEY,
    date INTEGER NOT NULL
    );

CREATE TABLE reports (
    user_id INTEGER NOT NULL,
    match_id INTEGER NOT NULL,
    games INTEGER NOT NULL,
    deck TEXT,
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (match_id) REFERENCES matches (match_id)
    );



