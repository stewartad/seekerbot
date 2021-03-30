import os
from re import split

from discord.ext.commands.errors import BadArgument
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

class MatchReportConverter(commands.Converter):
    def __init__(self) -> None:
        super().__init__()
        self.user1 = {
            'id': '',
            'score': 0 
        }
        self.user2 = {
            'id': '',
            'score': 0
        }

    def _get_report_string(self):
        players = [self.user1, self.user2] if self.user1['score'] >= self.user2['score'] else [self.user2, self.user1]
        return f"Match Report: {players[0]['id'].mention} {players[0]['score']}-{players[1]['score']} {players[1]['id'].mention}"
    
    async def convert(self, ctx: commands.Context, argument: str):
        # split string by spaces
        split_cmd = argument.split(' ')

        # get users
        member_converter = commands.MemberConverter()
        self.user1['id'] = await member_converter.convert(ctx, split_cmd[0])
        self.user2['id'] = await member_converter.convert(ctx, split_cmd[2])

        # parse scores for two supported formats
        failed = False
        try:
            # <user1> X <user2> Y <description>
            _ = int(split_cmd[1], 10)
            self.user1['score'] = split_cmd[1]
            self.user2['score'] = split_cmd[3]
        except ValueError:
            failed = True

        if failed:
            try:
                # <user1> X-Y <user2>
                scores = split_cmd[1].split('-')
                self.user1['score'] = int(scores[0])
                self.user2['score'] = int(scores[1]) 
            except ValueError:
                # Could not find a score
                raise BadArgument()

        report_match(ctx.guild.id, self.user1, self.user2)
        return self._get_report_string()

class Seeker(commands.Cog):
    
    def __init__(self):
        pass

    @commands.command(name='undo')
    async def undo(self, ctx):
        pass

    @undo.error
    async def undo_error(self, ctx, error):
        pass

    @commands.command(name='report')
    async def report(self, ctx, *, report: MatchReportConverter):
        await ctx.send(report)

    @report.error
    async def report_error(self, ctx, err):
        pass

    @commands.command(name='stats')
    async def stats(self, ctx, user: User):
        pass

    @stats.error
    async def stats_error(self, ctx, err):
        pass

    @commands.command(name='leaderboard')
    async def leaderboard(self, ctx, count: typing.Optional[int] = 10, time: typing.Optional[str] = 'week'):
        pass

    @leaderboard.error
    async def leaderboard_error(self, ctx, err):
        pass

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
async def report(ctx, *, report: MatchReportConverter):
    await ctx.send(report)

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

bot.run(TOKEN)
