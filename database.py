import sqlite3
import os
from util import get_starting_timestamp
from discord.user import User
from dotenv import load_dotenv

def report_match(guild_id: int, user1: User, user1_games: int, user2: User, user2_games: int):
    db = _check_db(guild_id)

    _create_user_entry(db, user1)
    _create_user_entry(db, user2)
    match_id = _create_match_entry(db)
    _create_report_entry(db, user1, match_id, user1_games)
    _create_report_entry(db, user2, match_id, user2_games)

def _check_db(guild_id: int):
    db = f'{guild_id}.db'
    if not os.path.exists(db):
        _create_db(db)
    return db

def _create_db(database: str):
    conn = sqlite3.connect(database)
    c = conn.cursor()
    c.executescript('''
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
    ''')
    conn.commit()
    c.close()
    conn.close()

def _create_user_entry(db: str, user: User):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT user_id FROM users WHERE user_id=(?)', (user.id,))
    if c.fetchone() is None:
        statement = '''INSERT INTO users (user_id, name) VALUES (?, ?)'''
        c.execute(statement, (user.id, str(user)))
        conn.commit()
    c.close()
    conn.close()

def _create_match_entry(db: str):
    conn = sqlite3.connect(db)
    statement = '''INSERT INTO matches (date) VALUES (strftime('%s', 'now'))'''
    c = conn.cursor()
    c.execute(statement)
    match_id = c.lastrowid
    conn.commit()
    c.close()
    conn.close()
    return match_id

def _create_report_entry(db: str, user: User, match_id: int, games: int):
    conn = sqlite3.connect(db)
    statement = '''INSERT INTO reports (user_id, match_id, games) VALUES(?, ?, ?)'''
    c = conn.cursor()
    c.execute(statement, (user.id, match_id, games))
    conn.commit()
    c.close()
    conn.close()

def get_leaderboard(guild_id: int, time: str):
    db = _check_db(guild_id)
    timestamp = get_starting_timestamp(time)
    conn = sqlite3.connect(db)
    statement = f'''SELECT DISTINCT name, SUM(w.games + l.games), SUM(w.games)
                    FROM reports w
                    INNER JOIN reports l ON w.match_id = l.match_id AND w.user_id <> l.user_id
                    INNER JOIN users ON w.user_id = users.user_id
                    INNER JOIN matches ON w.match_id = matches.match_id
                    WHERE matches.date >= {timestamp}
                    GROUP BY w.user_id
                    ORDER BY SUM(w.games + l.games) DESC;
                '''
    c = conn.cursor()
    c.execute(statement)
    results = c.fetchall()
    c.close()
    conn.close()
    return results

def get_stat(guild_id: int, time: str, user: int):
    db = _check_db(guild_id)
    timestamp = get_starting_timestamp(time)
    conn = sqlite3.connect(db)
    statement = f'''
                SELECT SUM(w.games + l.games), SUM(w.games)
                FROM reports w
                INNER JOIN reports l ON w.match_id = l.match_id AND w.user_id <> l.user_id
                INNER JOIN users ON w.user_id = users.user_id
                INNER JOIN matches ON w.match_id = matches.match_id
                WHERE matches.date >= {timestamp} AND w.user_id = {user}
                '''
    c = conn.cursor()
    c.execute(statement)
    results = c.fetchone()
    c.close()
    conn.close()
    return results