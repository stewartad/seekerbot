import sqlite3
import discord
import os
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

def create_match_entry():
    conn = sqlite3.connect(MATCH_DB)
    statement = '''INSERT INTO matches (date) VALUES (strftime('%s', 'now'))'''
    c = conn.cursor()
    c.execute(statement)
    match_id = c.lastrowid
    conn.commit()
    c.close()
    return match_id

def create_report_entry(user: User, match_id: int, games: int, deck: str):
    conn = sqlite3.connect(MATCH_DB)
    statement = '''INSERT INTO reports (user_id, match_id, games, deck) VALUES(?, ?, ?, ?)'''
    c = conn.cursor()
    c.execute(statement, (user.id, match_id, games, deck))
    conn.commit()
    c.close()

def get_leaderboard():
    conn = sqlite3.connect(MATCH_DB)
    statement = '''SELECT name, count(user_id) 
                FROM users, reports 
                GROUPBY reports.user_id
                ORDERBY count(reports.user_id)
                WHERE users.user_id = reports.user_id
                '''

@bot.event
async def on_ready():
    for guild in bot.guilds:
        print(guild)

@bot.command(name='report')
async def report(ctx, user1: User, user1_games: int, user1_deck: str, user2: User, user2_games: int, user2_deck: str):
    create_user_entry(user1)
    create_user_entry(user2)
    match_id = create_match_entry()
    create_report_entry(user1, match_id, user1_games, user1_deck)
    create_report_entry(user2, match_id, user2_games, user2_deck)

    
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
    pass

bot.run(TOKEN)
