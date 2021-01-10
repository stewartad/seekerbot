from datetime import datetime, timedelta

def get_starting_timestamp(time):
    now = datetime.today()
    if time == 'week':
        weekstart = now - timedelta(days=now.weekday())
        return weekstart.timestamp()
    elif time == 'month':
        return now.replace(day = 1).timestamp()
    elif time == 'year':
        return now.replace(month=1, day=1).timestamp()
    else:
        return 0