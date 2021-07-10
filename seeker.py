import os

from discord.ext.commands.errors import BadArgument
from database import *
from discord.user import User
from dotenv import load_dotenv
from discord.ext import commands
import typing
from seekerhelper import SeekerHelper
import requests

load_dotenv()
helper = SeekerHelper()
API_HOST= os.getenv('API_HOST')
ADMIN = os.getenv('API_USER')
PASSWD = os.getenv('API_PASSWD')
BASE_URL = API_HOST + '/seekerbot/api'

class MatchReportConverter(commands.Converter):

    async def convert(self, ctx: commands.Context, argument: str):
        # split string by spaces
        args = argument.split(' ')

        # <user1> X <user2> Y <description>
        # <user1> <deck> X <user2> <deck> Y <description>
        # <user1> X-Y <user2> <description>
        # <user1> <deck> X-Y <user2> <deck> <description>

        # Comnmands are always user deck score

        match = {
            'reports': [],
            'channel_id': ctx.channel.id,
            'guild': {
                'guild_id': ctx.guild.id,
                'name': ctx.guild.name
            },
        }

        # scan args for members, associate non-member strings with the most recently parsed member
        member_converter = commands.MemberConverter()
        last_user = None
        sorted_args = {}
        for arg in args:
            try:
                last_user = await member_converter.convert(ctx, arg)
                sorted_args[last_user] = []
            except BadArgument:
                if last_user is None:
                    raise BadArgument()
                else:
                    sorted_args[last_user].append(arg)

        # if members are less than 2, this is an invalid command
        if len(sorted_args.keys()) < 2:
            raise BadArgument()

        for user, data in sorted_args.items():
            report = {
                'user': {
                    'user_id': user.id,
                    'name': f'{user.name}#{user.discriminator}'
                },
                'games': '',
                'deck': '',
                # 'description': '',
            }

            if len(sorted_args.keys()) == 2:
                # scores = args[1].split('-')
                pass

            # find score, deck, and description
            for i, arg in enumerate(data):
                try:
                    report['games'] = int(arg)
                except ValueError:
                    if report['deck'] == '':
                        report['deck'] = arg
                    # elif user == last_user and i < len(data) + 1:
                    #     report['description'] = data[i + 1]
                    else:
                        raise BadArgument()

            if report['games'] == '':
                raise BadArgument()

            match['reports'].append(report)

        # print(match)

        report_req = requests.post(f'{BASE_URL}/matches/', json=match, auth=(ADMIN, PASSWD))
        print(report_req.text)
        if report_req.status_code != 201:
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

    @commands.command(name='report')
    async def report(self, ctx, *, report: MatchReportConverter):
        '''
        !report @<user1> X @<user2> Y OR
        !report @<user1> X-Y @<user2>
        '''
        await ctx.send(report)

    @commands.command(name='stats')
    async def stats(self, ctx, user: User):
        '''
        `!stats @<user>`
        '''

        guild_id = 315538837474508800
        stats_req = requests.get(f'{BASE_URL}/leaderboard/{user.id}', params={'guild_id': guild_id})
        if stats_req.status_code != 200:
            return f'User {user} not found'
        stats = stats_req.json()
        header_fmt = '{:>9}\t {:<6} {:<6} {:6}'
        entry_fmt = '{:>9}\t {:<6} {:<6} {:.2%}'

        entries = [entry_fmt.format(time, stats.get('games_played'), stats.get('games_won'), stats.get('winrate')) for time in self.timeframes]
        # wins = stats.get(time.upper()).get('games_won')
        # games = stats.get(time.upper()).get('games_played')
        # winrate = stats.get(time.upper()).get('winrate')
            
        message = f'''```Stats for {user}\n{header_fmt.format('Timeframe', 'Games', 'Won', 'Win %')}\n{"\n".join(entries)}```'''
        await ctx.send(message)

    @commands.command(name='leaderboard')
    async def leaderboard(self, ctx, count: typing.Optional[int] = 10, time: typing.Optional[str] = 'week'):
        '''
        !leaderboard [count] [time]
        '''
        if time.upper() not in self.timeframes:
                await ctx.send('Invalid time. Use week, month, year, or all')
                return

        guild_id = 315538837474508800
        leaderboard = requests.get(f'{BASE_URL}/leaderboard', params={'guild_id': guild_id}).json()

        entry_fmt = '{:2}. {:<16} {:<6} {:<6} {:.2%}'
        header_fmt = '{:2}. {:<16} {:<6} {:<6} {:4}'
        entries = [entry_fmt.format(i + 1, entry.get('name')[:16], entry.get('games_played'), entry.get('games_won'), entry.get('winrate')) for i, entry in enumerate(leaderboard[:count])]
        
        message = f'''```{header_fmt.format('No', 'User', 'Games', 'Won', 'Win %')}\n{"\n".join(entries)}```'''
        await ctx.send(message)

    # async def cog_command_error(self, ctx, error):
    #     print(error)
    #     return await ctx.send(ctx.command.help)


TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    for guild in bot.guilds:
        print(str(guild) + ' ' + str(guild.id))

bot.add_cog(SeekerCog())
bot.run(TOKEN)
