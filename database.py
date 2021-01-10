import sqlite3
import os
from discord.user import User
from dotenv import load_dotenv

load_dotenv()
MATCH_DB = os.getenv('MATCH_DB')

def create_user_entry(user: User):
    conn = sqlite3.connect(MATCH_DB)
    c = conn.cursor()
    c.execute('SELECT user_id FROM users WHERE user_id=(?)', (user.id,))
    if c.fetchone() is None:
        statement = '''INSERT INTO users (user_id, name) VALUES (?, ?)'''
        c.execute(statement, (user.id, str(user)))
        conn.commit()
    c.close()
    conn.close()

def create_match_entry():
    conn = sqlite3.connect(MATCH_DB)
    statement = '''INSERT INTO matches (date) VALUES (strftime('%s', 'now'))'''
    c = conn.cursor()
    c.execute(statement)
    match_id = c.lastrowid
    conn.commit()
    c.close()
    conn.close()
    return match_id

def create_report_entry(user: User, match_id: int, games: int):
    conn = sqlite3.connect(MATCH_DB)
    statement = '''INSERT INTO reports (user_id, match_id, games) VALUES(?, ?, ?)'''
    c = conn.cursor()
    c.execute(statement, (user.id, match_id, games))
    conn.commit()
    c.close()
    conn.close()

def get_leaderboard(time: float):
    conn = sqlite3.connect(MATCH_DB)
    statement = f'''SELECT DISTINCT name, SUM(w.games + l.games), SUM(w.games)
                    FROM reports w
                    INNER JOIN reports l ON w.match_id = l.match_id AND w.user_id <> l.user_id
                    INNER JOIN users ON w.user_id = users.user_id
                    INNER JOIN matches ON w.match_id = matches.match_id
                    WHERE matches.date >= {time}
                    GROUP BY w.user_id
                    ORDER BY SUM(w.games + l.games);
                '''
    c = conn.cursor()
    c.execute(statement)
    results = c.fetchall()
    c.close()
    conn.close()
    return results

def get_stat(time: float, user: str):
    conn = sqlite3.connect(MATCH_DB)
    statement = f'''
                SELECT DISTINCT name, SUM(w.games + l.games)
                FROM reports w
                INNER JOIN reports l ON w.match_id = l.match_id AND w.user_id <> l.user_id
                INNER JOIN users ON w.user_id = users.user_id
                INNER JOIN matches ON w.match_id = matches.match_id
                WHERE matches.date >= {time} AND w.user_id = {user}
                '''
    c = conn.cursor()
    c.execute(statement)
    results = c.fetchall()
    c.close()
    conn.close()
    return results