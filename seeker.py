import sqlite3
import discord
import os
from discord.user import User
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('')

conn = sqlite3.connect('league.db')
bot = commands.Bot(command_prefix='!')

def setup_database():
    create_user_table = '''CREATE TABLE IF NOT EXISTS users
                        (user_id INTEGER PRIMARY KEY,
                        name TEXT NOT_NULL)'''
    create_match_table = '''CREATE TABLE IF NOT EXISTS matches
                     (match_id INTEGER PRIMARY KEY AUTOINCREMENT,
                     date INTEGER NOT NULL)'''
    create_report_table = '''CREATE TABLE IF NOT EXISTS reports
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    match_id INTEGER NOT NULL,
                    games INTEGER NOT NULL,
                    deck TEXT,
                    FOREIGN KEY (user_id)
                        REFERENCES users (user_id),
                    FOREIGN KEY (match_id)
                        REFERENCES matches (match_id))
    '''
    c = conn.cursor()
    c.execute(create_user_table)
    c.execute(create_match_table)
    c.execute(create_report_table)
    conn.commit()
    c.close()

def create_user_entry(user: User):
    c = conn.cursor()
    statement = '''SELECT user_id FROM users WHERE user_id=(?)'''
    c.execute(statement, (user.id))
    if c.fetchone():
        return
    statement = '''INSERT INTO users (user_id, name) VALUES (?, ?)'''
    c.execute(statement, (user.id, str(user)))
    conn.commit()
    c.close()

def create_match_entry():
    statement = '''INSERT INTO matches (date) VALUES (strftime('%s', 'now'))'''
    c = conn.cursor()
    c.execute(statement)
    match_id = c.lastrowid
    conn.commit()
    c.close()
    return match_id

def create_report_entry(user: User, match_id: int, games: int, deck: str):
    statement = '''INSERT INTO reports (user_id, match_id, games, deck) VALUES(?, ?, ?, ?)'''
    c = conn.cursor()
    c.execute(statement, (user.id, match_id, games, deck))
    conn.commit()
    c.close()

@bot.event
async def on_ready():
    for guild in bot.guilds:
        print(guild)
        if guild.name == GUILD:
            break
    setup_database()

@bot.command(name='report')
async def report(ctx, user1: User, user1_games: int, user1_deck: str, user2: User, user2_games: int, user2_deck: str):
    create_user_entry(user1)
    create_user_entry(user2)
    match_id = create_match_entry()
    create_report_entry(user1, match_id, user1_games, user1_deck)
    create_report_entry(user2, match_id, user2_games, user2_deck)

    if (user1 in bot.users):
        print(user1)
        print(user1.id)
        print(user1.mention)
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
    message = f"{match_report['winner'].mention} {match_report['winner_games']}-{match_report['loser_games']} {match_report['loser'].mention}"
    await ctx.send(message)

@bot.command(name='stats')
async def stats(ctx, user, time='week'):
    pass

@bot.command(name='leaderboard')
async def leaderboard(ctx):
    pass

bot.run(TOKEN)
