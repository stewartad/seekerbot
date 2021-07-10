from discord.user import User
from database import DbConn
import requests
import os

LINE = '\n'

class SeekerHelper:
    def __init__(self) -> None:
        self.host = os.getenv('API_HOST')
        self.base_url = self.host + '/seekerbot/api'
        self._data = {}
        self.timeframes = ['WEEK', 'MONTH', 'YEAR', 'ALL']

    def _get_database(self, guild_id: int) -> DbConn:
        if self._data.get(guild_id) is None:
            self._data[guild_id] = DbConn(guild_id)
        return self._data[guild_id]

    def undo(self, guild_id, user: User):
        db = self._get_database(guild_id)
        results = db.undo_last_report(user.id)
        if results is None:
            return 'Matches can only be undone within 5 minutes of the report.'
        else:
            return f'{user.mention}\'s most recent match deleted.'

    # def report_match(self, guild_id: int, user1: dict, user2: dict):
    #         db = self._get_database(guild_id)
    #         db.create_user(user1['id'])
    #         db.create_user(user2['id'])
    #         match_id = db.create_match()
    #         db.create_report(user1['id'], match_id, user1['games'])
    #         db.create_report(user2['id'], match_id, user2['games'])
            
    #         players = [user1, user2] if user1['games'] >= user2['games'] else [user2, user1]
    #         return f"Match Report: {players[0]['id'].mention} {players[0]['games']}-{players[1]['games']} {players[1]['id'].mention}"
    