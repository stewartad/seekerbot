# from datetime import date, time, datetime, timedelta, timezone
# from dateutil import tz

# def get_starting_timestamp(timeframe):
#     now = datetime.combine(date.today(), time(0, 0, 0, 0, timezone.utc), timezone.utc)
#     if timeframe == 'week':
#         weekstart = now - timedelta(days=now.weekday())
#         return weekstart.timestamp()
#     elif timeframe == 'month':
#         return now.replace(day = 1).timestamp()
#     elif timeframe == 'year':
#         return now.replace(month=1, day=1).timestamp()
#     else:
#         return datetime(2018, 1, 1, 0, 0, 0, 0, timezone.utc).timestamp()

# def get_timestamps():
#     eastern_timezone = tz.gettz('America/New York')
#     now = datetime.combine(date.today(), time(0,0,0,0, eastern_timezone), eastern_timezone)
    
#     week = (now - timedelta(days=now.weekday())).timestamp()
#     month = now.replace(day=1).timestamp()
#     year = now.replace(month = 1, day = 1).timestamp()
#     all = datetime(2018, 1, 1, tzinfo=eastern_timezone).timestamp()

#     return week, month, year, all