import os

from discord.ext.commands.errors import BadArgument
from database import *
from discord.user import User
from dotenv import load_dotenv
from discord.ext import commands
import typing

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
        self.timeframes = ['WEEK', 'MONTH', 'YEAR', 'ALL']

    def _get_winrate(self, guild_id: int, time: str, user: int):
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

    @commands.command(name='undo')
    async def undo(self, ctx):
        '''
        !undo

        Undoes the last match played within the past hour in which the sender participated in
        '''
        user = ctx.author
        results = undo_last_report(ctx.guild.id, user.id)
        msg = ''
        if results is None:
            msg = 'Matches can only be undone within 5 minutes of the report.'
        else:
            msg = f'{user.mention}\'s most recent match deleted.'
        await ctx.send(msg)

    @commands.command(name='report')
    async def report(self, ctx, *, report: MatchReportConverter):
        '''
        USAGE:
        !report @<user1> X @<user2> Y OR
        !report @<user1> X-Y @<user2>
        '''
        await ctx.send(report)

    @commands.command(name='stats')
    async def stats(self, ctx, user: User):
        '''
        `!stats @<user>`
        '''
        if user not in bot.users:
            await ctx.send(f'User {user} not found')
            return
        header_str = '{:>9}\t {:<6} {:<6} {:6}'
        entry_str = '{:>9}\t {:<6} {:<6} {:.2%}'
        rows = [f'Stats for {user}', header_str.format('Timeframe', 'Games', 'Won', 'Win %')]

        for time in self.timeframes:
            won, total, winrate = self._get_winrate(ctx.guild.id, time.lower(), user.id)
            rows.append(entry_str.format(time, total, won, winrate))

        newline = '\n'
        message = f'```{newline.join(rows)}```'
        await ctx.send(message)

    @commands.command(name='leaderboard')
    async def leaderboard(self, ctx, count: typing.Optional[int] = 10, time: typing.Optional[str] = 'week'):
        '''
        
        '''
        results = get_leaderboard(ctx.guild.id, time)

        if time.upper() not in self.timeframes:
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

    async def cog_command_error(self, ctx, error):
        return await ctx.send(ctx.command.help)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    for guild in bot.guilds:
        print(guild)

bot.add_cog(Seeker())
bot.run(TOKEN)
