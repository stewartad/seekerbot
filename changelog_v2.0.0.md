# SeekerBot 2.0.0

## New Features

### New report syntax

### Per-Channel Reports
Matches reported to SeekerBot now record which channel they were reported in. Matches reported before v2.0.0 will not have a channel associated with them. Leaderboards will still track matches across all channels in a guild. 

### Tournament Reporting
As a part of per-channel reports 

### Primus Match Reporting
Primus matches can now be properly reported to SeekerBot. 


### Backend upgrades
SeekerBot now uses a REST API to report and retrieve data. This doesn't provide much functionality to users (yet) but enables more complex features in the future. In addition, databases are no longer separated by guild, which will enable tracking matches across guilds in the future. 

## Other Changes

- Cutoffs for league play now follow EST timezone
- Added help text with examples for each command
- Undo time limit is now 1 hour