import os

from discord.ext.commands.errors import BadArgument
from database import *
from discord.user import User
from dotenv import load_dotenv
from discord.ext import commands
import typing
from seekerhelper import SeekerHelper

helper = SeekerHelper()

class MatchReportConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, argument: str):
        # split string by spaces
        split_cmd = argument.split(' ')
        user1 = {
            'id': '',
            'score': 0 
        }
        user2 = {
            'id': '',
            'score': 0
        }

        # get users
        member_converter = commands.MemberConverter()
        user1['id'] = await member_converter.convert(ctx, split_cmd[0])
        user2['id'] = await member_converter.convert(ctx, split_cmd[2])

        # parse scores for two supported formats
        failed = False
        try:
            # <user1> X <user2> Y <description>
            _ = int(split_cmd[1], 10)
            user1['score'] = split_cmd[1]
            user2['score'] = split_cmd[3]
        except ValueError:
            failed = True

        if failed:
            try:
                # <user1> X-Y <user2>
                scores = split_cmd[1].split('-')
                user1['score'] = int(scores[0])
                user2['score'] = int(scores[1]) 
            except ValueError:
                # Could not find a score
                raise BadArgument()

        return helper.report_match(ctx.guild.id, user1, user2)
        

class SeekerCog(commands.Cog):
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
        message = helper.stats(ctx.guild.id, user)
        await ctx.send(message)

    @commands.command(name='leaderboard')
    async def leaderboard(self, ctx, count: typing.Optional[int] = 10, time: typing.Optional[str] = 'week'):
        '''
        
        '''
        message = helper.leaderboard(ctx.guild.id, count, time)
        await ctx.send(message)

    # async def cog_command_error(self, ctx, error):
    #     print(error)
    #     return await ctx.send(ctx.command.help)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    for guild in bot.guilds:
        print(str(guild) + ' ' + str(guild.id))

bot.add_cog(SeekerCog())
bot.run(TOKEN)
