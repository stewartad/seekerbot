# Small Improvements

- [x] fix leaderboard formatting
- [x] all-time leaderboard
- [x] customizable leaderboard cutoff
- [ ] user stats with overall place
- [x] undo last report feature
- [ ] more precise time controls
- [ ] get total games for a given time period

# Large Scale
- [ ] Frontend website
- [ ] event reporting

# v1.3 features
	- [x] Seeker Commands in a Cog
	- [x] allow second match report syntax
	- [x] parse match report in a Converter
	- [ ] record deck names
	- [ ] proper help responses
	- [ ] improved database management

# v2.0 features
	- [ ] Rest API

# v2.1 features
	- [ ] Tournament Reporting

# Per-channel reports
	- Add channel column to matches table
	   - update all current matches to the league channel (vectorsigma) + casual reports channel (bayformers) - *once down for maintenance*
	- Log channel id on each report
	- Leaderboard shows reports for only that channel
	- Add channels to be tracked (admin feature)

# Winrate leaderboard
	- By default, leaderboard does not show winrate
	- a winrate argument will show it

# Deck logging
	- reports can have a deck added for each player
	- for playtesting, enforce that the deck name is from a list of strings