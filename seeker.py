from datetime import date, timezone
import enum
import os
import re

from discord.ext.commands.errors import BadArgument, UserNotFound
from database import *
from util import get_timestamps
from discord.user import User
from dotenv import load_dotenv
from discord.ext import commands
import typing
from seekerhelper import SeekerHelper
import requests
import logging

load_dotenv()
helper = SeekerHelper()
API_HOST= os.getenv('API_HOST')
ADMIN = os.getenv('API_USER')
PASSWD = os.getenv('API_PASSWD')
BASE_URL = API_HOST + '/seekerbot/api'
NL = '\n'


class NoGamesRecordedError(Exception):
    def __init__(self, user, *args: object) -> None:
        self.user = user
        self.message = f'No games on record for {self.user} in this guild.'
        super().__init__(*args)

    def __str__(self) -> str:
        return f'No games on record for {self.user} in this guild.'


class MatchReportConverter(commands.Converter):

    async def convert(self, ctx: commands.Context, argument: str):
        # split string by spaces
        cmd_params = argument.split(' ')

        # <user1> X <user2> Y <description>
        # <user1> X <deck> <user2> Y <deck>

        # Comnmands are always user score deck

        # scan args for members, associate non-member strings with the most recently parsed member
        member_converter = commands.MemberConverter()
        cmd_params_len = len(cmd_params)
        sorted_args = {}

        user_pattern = re.compile('<@!\d+>')

        # get_users
        for i in range(cmd_params_len):
            param = cmd_params[i]
            if user_pattern.match(param):
                sorted_args[i] = {
                        'user': param,
                        'games': int(cmd_params[i+1])
                }

                deck_strs = []
                deck_first = i + 2
                deck_last = deck_first
                while deck_last >= deck_first and deck_last < cmd_params_len:
                    if not user_pattern.match(cmd_params[deck_last]):
                        deck_strs.append(cmd_params[deck_last])
                        deck_last += 1
                    else:
                        break
                    

                if deck_last > deck_first:
                    sorted_args[i]['deck'] = " ".join(cmd_params[deck_first:deck_last])

        # if members are less than 2, this is an invalid command
        if len(sorted_args.keys()) < 2:
            raise BadArgument("Not enough users in game")

        # construct match report
        match = {
            'reports': [],
            'channel_id': ctx.channel.id,
            'guild': {
                'guild_id': ctx.guild.id,
                'name': ctx.guild.name
            },
        }

        for data in sorted_args.values():
            user = data.get('user')
            try:
                converted_user = await member_converter.convert(ctx, user)
                report = {
                'user': {
                    'user_id': converted_user.id,
                    'name': f'{converted_user.name}#{converted_user.discriminator}'
                },
                'games': data.get('games'),
                'deck': data.get('deck')
            }
            except BadArgument:
                raise BadArgument(f'Invalid user: {user}')
            
            match['reports'].append(report)

        # print(match)

        report_req = requests.post(f'{BASE_URL}/matches/', json=match, auth=(ADMIN, PASSWD))
        print(report_req.text)
        if report_req.status_code != 201:
            logging.error(report_req.status_code)
            return 'Server Error'
        # msg = f"Match Report: {players[0]['id'].mention} {players[0]['score']}-{players[1]['score']} {players[1]['id'].mention}"
        report_str = [f"{rep.get('user').get('name')} - {rep.get('games')}" for rep in match['reports']]
        return f'Match Reported: {", ".join(report_str)}'


class SeekerCog(commands.Cog):
    def __init__(self) -> None:
        self.timeframes = ['WEEK', 'MONTH', 'YEAR', 'ALL']
        super().__init__()

    @commands.command(name='undo')
    async def undo(self, ctx: commands.Context):
        '''
        !undo

        Undoes the last match played within the past hour in which the sender participated in
        '''
        message = helper.undo(ctx.guild.id, ctx.author)
        await ctx.send(message)

    @undo.error
    async def undo_error(self, ctx, error):
        await ctx.send(str(error))

    @commands.command(name='report')
    async def report(self, ctx, *, report: MatchReportConverter):
        '''
        !report @<user1> X @<user2> Y OR
        !report @<user1> X-Y @<user2>
        '''
        await ctx.send(report)

    @report.error
    async def report_error(self, ctx, error):
        logging.exception('')
        await ctx.send(f'Error: {str(error)}')

    @commands.command(name='stats')
    async def stats(self, ctx, user: User):
        '''
        `!stats @<user>`
        '''

        guild_id = ctx.guild.id
        # guild_id = 315538837474508800

        header_fmt = '{:>9}\t {:<6} {:<6} {:6}'
        entry_fmt = '{:>9}\t {:<6} {:<6} {:.2%}'
        entries = []

        for i, time in enumerate(get_timestamps()):
            stats_req = requests.get(f'{BASE_URL}/leaderboard/{user.id}', params={'guild': guild_id, 'date': int(time)}, auth=(ADMIN, PASSWD))

            if not stats_req.ok:
                raise NoGamesRecordedError(user)

            stats = stats_req.json()
            entries.append(entry_fmt.format(self.timeframes[i], stats.get('games_played'), stats.get('games_won'), stats.get('winrate')))

        # entries = [entry_fmt.format(time, stats[i].get('games_played'), stats[i].get('games_won'), stats[i].get('winrate')) for i, time in enumerate(self.timeframes)]
            
        message = f'''```Stats for {user}{NL}{header_fmt.format('Timeframe', 'Games', 'Won', 'Win %')}{NL}{NL.join(entries)}```'''
        await ctx.send(message)

    @stats.error
    async def stats_error(self, ctx, error):
        logging.exception('')
        await ctx.send(f'Error: {error.original}')

    @commands.command(name='leaderboard')
    async def leaderboard(self, ctx, count: typing.Optional[int] = 10, time: typing.Optional[str] = 'week'):
        '''
        !leaderboard [count] [time]
        '''
        if time.upper() not in self.timeframes:
                await ctx.send('Invalid time. Use week, month, year, or all')
                return

        guild_id = ctx.guild.id
        # guild_id = 315538837474508800
        leaderboard_req = requests.get(f'{BASE_URL}/leaderboard', params={'guild': guild_id}, auth=(ADMIN, PASSWD))
        leaderboard = leaderboard_req.json()

        if leaderboard_req.status_code != 200:
            raise requests.RequestException(f'Error: response {leaderboard_req.status_code}')

        print(leaderboard)

        entry_fmt = '{:2}. {:<16} {:<6} {:<6} {:.2%}'
        header_fmt = '{:2}. {:<16} {:<6} {:<6} {:4}'
        entries = [entry_fmt.format(i + 1, entry.get('name')[:16], entry.get('games_played'), entry.get('games_won'), entry.get('winrate')) for i, entry in enumerate(leaderboard[:count])]
        
        message = f'''```{header_fmt.format('No', 'User', 'Games', 'Won', 'Win %')}{NL}{NL.join(entries)}```'''
        await ctx.send(message)

    @leaderboard.error
    async def leaderboard_error(self, ctx, error):
        logging.exception('')
        await ctx.send(f'Error: {str(error)}')

    @commands.command(name='decks')
    async def decks(self, ctx, count: typing.Optional[int] = 10, time: typing.Optional[str] = 'week'):
        '''
        !leaderboard [count] [time]
        '''
        if time.upper() not in self.timeframes:
                await ctx.send('Invalid time. Use week, month, year, or all')
                return

        guild_id = ctx.guild.id
        # guild_id = 315538837474508800
        leaderboard_req = requests.get(f'{BASE_URL}/decks', 
            params={
                'guild': ctx.guild.id,
                'channel_id': ctx.channel.id
                }, 
            auth=(ADMIN, PASSWD))
        leaderboard = leaderboard_req.json()

        if leaderboard_req.status_code != 200:
            raise requests.RequestException(f'Error: response {leaderboard_req.status_code}')

        print(leaderboard)

        entry_fmt = '{:2}. {:<16} {:<6} {:<6} {:.2%}'
        header_fmt = '{:2}. {:<16} {:<6} {:<6} {:4}'
        entries = [entry_fmt.format(i + 1, entry.get('deck')[:16], entry.get('games_played'), entry.get('games_won'), entry.get('winrate')) for i, entry in enumerate(leaderboard[:count])]
        
        message = f'''```{header_fmt.format('No', 'User', 'Games', 'Won', 'Win %')}{NL}{NL.join(entries)}```'''
        await ctx.send(message)


TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    for guild in bot.guilds:
        print(str(guild) + ' ' + str(guild.id))

bot.add_cog(SeekerCog())
bot.run(TOKEN)
