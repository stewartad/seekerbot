from datetime import datetime

def get_starting_timestamp(time):
    now = datetime.now()
    if time == 'week':
        now_iso = now.isocalendar()
        return datetime.fromisocalendar(now_iso[0], now_iso[1], 1).timestamp()
    elif time == 'month':
        return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).timestamp()
    elif time == 'year':
        return now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0).timestamp()
    else:
        return None