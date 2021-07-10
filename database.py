import sqlite3
import os
from util import get_starting_timestamp
from discord.user import User
from datetime import datetime, timedelta
# from sql_constants import *

CREATE_DB = '''
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
        );'''

GET_USER = 'SELECT user_id FROM users WHERE user_id=(?)'

CREATE_USER = 'INSERT INTO users (user_id, name) VALUES (?, ?)'

CREATE_MATCH = 'INSERT INTO matches (date) VALUES (strftime("%s", "now"))'

CREATE_REPORT = 'INSERT INTO reports (user_id, match_id, games) VALUES(?, ?, ?)'

GET_LEADERBOARD = '''
        SELECT DISTINCT name, SUM(w.games + l.games), SUM(w.games)
        FROM reports w
        INNER JOIN reports l ON w.match_id = l.match_id AND w.user_id <> l.user_id
        INNER JOIN users ON w.user_id = users.user_id
        INNER JOIN matches ON w.match_id = matches.match_id
        WHERE matches.date >= ?
        GROUP BY w.user_id
        ORDER BY SUM(w.games + l.games) DESC, SUM(w.games) DESC, name;
        '''

GET_STATS = '''
        SELECT SUM(w.games + l.games), SUM(w.games)
        FROM reports w
        INNER JOIN reports l ON w.match_id = l.match_id AND w.user_id <> l.user_id
        INNER JOIN users ON w.user_id = users.user_id
        INNER JOIN matches ON w.match_id = matches.match_id
        WHERE matches.date >= ? AND w.user_id = ?
        '''

GET_LAST_REPORT = '''
        SELECT m.match_id
        FROM matches m
        INNER JOIN reports ON m.match_id = reports.match_id
        WHERE m.date >= ? AND reports.user_id = ?
        ORDER BY m.date DESC
        LIMIT 1
        '''

DELETE_MATCH = '''
        DELETE FROM matches
        WHERE match_id = ?
        '''

DELETE_REPORT = '''
            DELETE FROM reports
            WHERE match_id = ?
            '''

class DbConn:
    '''
    Class for connecting to a database
    '''
    def __init__(self, guild_id) -> None:
        '''

        '''
        self.db = f'{guild_id}.db'
        if not os.path.exists(self.db):
            conn = sqlite3.connect(self.db)
            c = conn.cursor()
            c.execute(CREATE_DB)
            conn.commit()
            c.close()
            conn.close()
            

    def create_user(self, user: User):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute(GET_USER, (user.id,))
        if c.fetchone() is None:
            statement = '''INSERT INTO users (user_id, name) VALUES (?, ?)'''
            c.execute(statement, (user.id, str(user)))
            conn.commit()
        c.close()
        conn.close()

    def get_user(self, user_id):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute(GET_USER, (user_id,))
        return c.fetchone()

    def create_match(self):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute(CREATE_MATCH)
        match_id = c.lastrowid
        conn.commit()
        c.close()
        conn.close()
        return match_id

    def create_report(self, user: User, match_id: int, games: int):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute(CREATE_REPORT, (user.id, match_id, games))
        conn.commit()
        c.close()
        conn.close()

    def get_leaderboard(self, time: str) -> list:
        timestamp = get_starting_timestamp(time)
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute(GET_LEADERBOARD, (timestamp, ))
        results = c.fetchall()
        c.close()
        conn.close()

        return results

    def get_stats(self, time: str, user_id: int) -> tuple:
        '''
        Gets game totals for 
        '''
        timestamp = get_starting_timestamp(time)
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute(GET_STATS, (timestamp, user_id))
        results = c.fetchone()
        c.close()
        conn.close()
        wins = 0 if results[1] is None else float(results[1])
        games = 0 if results[0] is None else float(results[0])
        return wins, games

    def undo_last_report(self, user_id: int):
        timestamp = (datetime.now() - timedelta(minutes=5)).timestamp()
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute(GET_LAST_REPORT, (timestamp, user_id))

        results = c.fetchone()
        if results is None:
            return None
        match_id = results[0]

        c.execute(DELETE_MATCH, (match_id, ))
        c.execute(DELETE_REPORT, (match_id, ))
        
        conn.commit()
        c.close()
        conn.close()
        
