import os
from util import get_starting_timestamp
from database import *
from discord.user import User
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
MATCH_DB = os.getenv('MATCH_DB')

bot = commands.Bot(command_prefix='!')

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
async def stats(ctx, user):
    pass

@bot.command(name='leaderboard')
async def leaderboard(ctx, time='week'):
    timestamp = get_starting_timestamp(time)
    if timestamp is None:
        await ctx.send(f'Invalid time {time}')
        return
    results = get_leaderboard(timestamp)
    
    entry_str = '{:2}. {:<16} {:<6}'
    rows = [entry_str.format('No', 'User', 'Matches')]
    for idx, val in enumerate(results):
        rows.append(entry_str.format(idx+1, val[0], val[1]))
    newline = '\n'
    message = f'```{newline.join(rows)}```'
    await ctx.send(message)

bot.run(TOKEN)
