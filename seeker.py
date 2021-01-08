import sqlite3
import discord
import os
from datetime import datetime
from discord.user import User
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
MATCH_DB = 'league.db'

bot = commands.Bot(command_prefix='!')

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

def create_report_entry(user: User, match_id: int, games: int, deck: str):
    conn = sqlite3.connect(MATCH_DB)
    statement = '''INSERT INTO reports (user_id, match_id, games, deck) VALUES(?, ?, ?, ?)'''
    c = conn.cursor()
    c.execute(statement, (user.id, match_id, games, deck))
    conn.commit()
    c.close()
    conn.close()

def get_leaderboard(time: float):
    conn = sqlite3.connect(MATCH_DB)
    statement = f'''SELECT name, count(reports.user_id) 
                FROM users
                INNER JOIN reports ON users.user_id = reports.user_id
                INNER JOIN matches ON reports.match_id = matches.match_id
                WHERE matches.date >= {time}
                GROUP BY reports.user_id
                ORDER BY count(reports.user_id);
                '''
    c = conn.cursor()
    c.execute(statement)
    return c.fetchall()
    

@bot.event
async def on_ready():
    for guild in bot.guilds:
        print(guild)

@bot.command(name='report')
async def report(ctx, user1: User, user1_games: int, user2: User, user2_games: int):
    if user1 not in bot.users:
        await ctx.send(f'User {user1} not found')
        return
    if user2 not in bot.users:
        await ctx.send(f'User {user2} not found')
        return
    create_user_entry(user1)
    create_user_entry(user2)
    match_id = create_match_entry()
    create_report_entry(user1, match_id, user1_games)
    create_report_entry(user2, match_id, user2_games)

    match_report = {}
    if user1_games >= user2_games:
        match_report['winner'] = user1
        match_report['winner_games'] = user1_games
        match_report['loser'] = user2
        match_report['loser_games'] = user2_games
    else:
        match_report['winner'] = user2
        match_report['winner_games'] = user2_games
        match_report['loser'] = user1
        match_report['loser_games'] = user1_games
    message = f"Match Report: {match_report['winner'].mention} {match_report['winner_games']}-{match_report['loser_games']} {match_report['loser'].mention}"
    await ctx.send(message)

@bot.command(name='stats')
async def stats(ctx, user, time='week'):
    pass

@bot.command(name='leaderboard')
async def leaderboard(ctx, time='week'):
    now = datetime.now()
    start = now
    if time == 'week':
        now_iso = now.isocalendar()
        start = datetime.fromisocalendar(now_iso[0], now_iso[1], 1)
    elif time == 'month':
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif time == 'year':
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        await ctx.send(f'Invalid time {time}')
        return
    results = get_leaderboard(start.timestamp())
    
    
    entry_str = '{:2}. {:<16} {:<6}'
    rows = [entry_str.format('No', 'User', 'Matches')]
    for idx, val in enumerate(results):
        rows.append(entry_str.format(idx+1, val[0], val[1]))
    newline = '\n'
    message = f'```{newline.join(rows)}```'
    await ctx.send(message)

    
bot.run(TOKEN)
