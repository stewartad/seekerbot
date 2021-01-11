# SeekerBot
SeekerBot is a Discord bot used for tracking Transformers TCG match reports.

[Add to Your Server](https://discord.com/api/oauth2/authorize?client_id=797931758975975475&permissions=67584&scope=bot)

# Usage

## Report
Reports a single match result.

`!report @[user1] [games won] @[user2] [games won]`

For example:

`!report @player1 2 @player2 0`

## Stats
Queries the stats of a single user.

`!stats @[user1]`

## Leaderboard
Gets the users that won the most within the given time frame. Defaults to weekly leaderboards. 

`!leaderboard [week|month|year]`
