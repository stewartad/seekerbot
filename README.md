# SeekerBot
SeekerBot is a Discord bot used for tracking Transformers TCG match reports.

# Usage

## Report
Reports a single match result.

`!report @[user1] [games won] @[user2] [games won]`

For example:

`!report @player1 2 @player2 0`

## Stats
Queries the stats of a single user.

`!stats @user1`

## Leaderboard
Gets the users that won the most within the given time frame. Defaults to 10 entries in a weekly leaderboard. 

`!leaderboard [# of entries] [week|month|year|all]`