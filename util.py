from datetime import date, time, datetime, timedelta, timezone

def get_starting_timestamp(timeframe):
    now = datetime.combine(date.today(), time(0, 0, 0, 0, timezone.utc), timezone.utc)
    if timeframe == 'week':
        weekstart = now - timedelta(days=now.weekday())
        return weekstart.timestamp()
    elif timeframe == 'month':
        return now.replace(day = 1).timestamp()
    elif timeframe == 'year':
        return now.replace(month=1, day=1).timestamp()
    else:
        return datetime(2018, 1, 1, 0, 0, 0, 0, timezone.utc)