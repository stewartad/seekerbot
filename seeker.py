import os
from util import get_starting_timestamp
from database import *
from discord.user import User
from dotenv import load_dotenv
from discord.ext import commands
import typing

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')
timeframes = ['week', 'month', 'year', 'all']

@bot.event
async def on_ready():
    for guild in bot.guilds:
        print(guild)

@bot.command(name='undo')
async def undo(ctx):
    user = ctx.author
    results = undo_last_report(ctx.guild.id, user.id)
    msg = ''
    if results is None:
        msg = 'Matches can only be undone within 5 minutes of the report.'
    else:
        msg = f'{user.mention}\'s most recent match deleted.'
    await ctx.send(msg)

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

    won, total, winrate = _get_winrate(ctx.guild.id, 'week', user.id)
    rows.append(entry_str.format('Week', total, won, winrate))

    won, total, winrate = _get_winrate(ctx.guild.id, 'month', user.id)
    rows.append(entry_str.format('Month', total, won, winrate))

    won, total, winrate = _get_winrate(ctx.guild.id, 'year', user.id)
    rows.append(entry_str.format('Year', total, won, winrate))

    won, total, winrate = _get_winrate(ctx.guild.id, '', user.id)
    rows.append(entry_str.format('All Time', total, won, winrate))

    newline = '\n'
    message = f'```{newline.join(rows)}```'
    await ctx.send(message)

@bot.command(name='leaderboard')
async def leaderboard(ctx, count: typing.Optional[int] = 10, time: typing.Optional[str] = 'week'):
    results = get_leaderboard(ctx.guild.id, time)

    if time not in timeframes:
        await ctx.send('Invalid time. Use week, month, year, or all')
        return
    
    header_str = '{:2}. {:<16} {:<6} {:<6} {:4}'
    entry_str = '{:2}. {:<16} {:<6} {:<6} {:.2%}'
    rows = [header_str.format('No', 'User', 'Games', 'Won', 'Win %')]
    for idx, val in enumerate(results[:count]):
        winrate = float(val[2]) / float(val[1])
        rows.append(entry_str.format(idx+1, val[0][:16], val[1], val[2], winrate))
    newline = '\n'
    message = f'```{newline.join(rows)}```'
    await ctx.send(message)

def _get_winrate(guild_id: int, time: str, user: int):
    result = get_stat(guild_id, time, user)

    won_games = result[1]
    if won_games is None:
        won_games = 0
    else:
        won_games = float(result[1])

    total_games = result[0]
    if total_games is None:
        total_games = 0
    else:
        total_games = float(result[0])

    if total_games == 0:
        winrate = 0
    else:
        winrate = won_games / total_games
    return won_games, total_games, winrate

bot.run(TOKEN)
