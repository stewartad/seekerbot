from discord.user import User
from database import DbConn

class SeekerHelper:
    def __init__(self) -> None:
        self._data = {}
        self.timeframes = ['WEEK', 'MONTH', 'YEAR', 'ALL']

    def _get_database(self, guild_id: int) -> DbConn:
        if self._data.get(guild_id) is None:
            self._data[guild_id] = DbConn(guild_id)
        return self._data[guild_id]

    def leaderboard(self, guild_id: int, count: int, time: str):
            '''
            
            '''
            if time.upper() not in self.timeframes:
                return 'Invalid time. Use week, month, year, or all'

            db = self._get_database(guild_id)
            results = db.get_leaderboard(time)
            
            header_str = '{:2}. {:<16} {:<6} {:<6} {:4}'
            entry_str = '{:2}. {:<16} {:<6} {:<6} {:.2%}'
            rows = [header_str.format('No', 'User', 'Games', 'Won', 'Win %')]
            for idx, val in enumerate(results[:count]):
                user = val[0]
                games = val[1]
                wins = val[2]

                winrate = wins / games if games != 0 else 0
                rows.append(entry_str.format(idx+1, user[:16], games, wins, winrate))
            newline = '\n'
            return f'```{newline.join(rows)}```'

    def undo(self, guild_id, user: User):
        db = self._get_database(guild_id)
        results = db.undo_last_report(user.id)
        if results is None:
            return 'Matches can only be undone within 5 minutes of the report.'
        else:
            return f'{user.mention}\'s most recent match deleted.'

    def stats(self, guild_id, user: User):
        db = self._get_database(guild_id)
        if db.get_user(user.id) is None:
            return f'User {user} not found'
        header_str = '{:>9}\t {:<6} {:<6} {:6}'
        entry_str = '{:>9}\t {:<6} {:<6} {:.2%}'
        rows = [f'Stats for {user}', header_str.format('Timeframe', 'Games', 'Won', 'Win %')]

        for time in self.timeframes:
            wins, games = db.get_stats(time, user.id)
            winrate = wins / games if games != 0 else 0
            rows.append(entry_str.format(time, games, wins, winrate))
        newline = '\n'
        return f'```{newline.join(rows)}```'

    def report_match(self, guild_id: int, user1: dict, user2: dict):
        db = self._get_database(guild_id)
        db.create_user(user1['id'])
        db.create_user(user2['id'])
        match_id = db.create_match()
        db.create_report(user1['id'], match_id, user1['score'])
        db.create_report(user2['id'], match_id, user2['score'])
        
        players = [user1, user2] if user1['score'] >= user2['score'] else [user2, user1]
        return f"Match Report: {players[0]['id'].mention} {players[0]['score']}-{players[1]['score']} {players[1]['id'].mention}"

    