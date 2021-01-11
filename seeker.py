import os
from util import get_starting_timestamp
from database import *
from discord.user import User
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

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
    report_match(ctx.guild.id, user1, user1_games, user2, user2_games)

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
async def stats(ctx, user: User):
    if user not in bot.users:
        await ctx.send(f'User {user} not found')
        return
    
    header_str = '{:>9}\t {:<6} {:<6} {:6}'
    entry_str = '{:>9}\t {:<6} {:<6} {:.2%}'
    rows = [f'Stats for {user}', header_str.format('Timeframe', 'Games', 'Won', 'Win %')]

    result = get_stat(ctx.guild.id, 'week', user.id)
    winrate = float(result[1]) / float(result[0])
    rows.append(entry_str.format('Week', result[0], result[1], winrate))

    result = get_stat(ctx.guild.id, 'month', user.id)
    winrate = float(result[1]) / float(result[0])
    rows.append(entry_str.format('Month', result[0], result[1], winrate))

    result = get_stat(ctx.guild.id, 'year', user.id)
    winrate = float(result[1]) / float(result[0])
    rows.append(entry_str.format('Year', result[0], result[1], winrate))

    result = get_stat(ctx.guild.id, '', user.id)
    winrate = float(result[1]) / float(result[0])
    rows.append(entry_str.format('All Time', result[0], result[1], winrate))

    newline = '\n'
    message = f'```{newline.join(rows)}```'
    await ctx.send(message)

@bot.command(name='leaderboard')
async def leaderboard(ctx, time='week'):
    results = get_leaderboard(ctx.guild.id, time)
    
    header_str = '{:2}. {:<16} {:<6} {:<6} {:4}'
    entry_str = '{:2}. {:<16} {:<6} {:<6} {:.2%}'
    rows = [header_str.format('No', 'User', 'Games', 'Won', 'Win %')]
    for idx, val in enumerate(results):
        winrate = float(val[2]) / float(val[1])
        rows.append(entry_str.format(idx+1, val[0], val[1], val[2], winrate))
    newline = '\n'
    message = f'```{newline.join(rows)}```'
    await ctx.send(message)

bot.run(TOKEN)
