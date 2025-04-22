import datetime
from odoo.exceptions import UserError

def parse_hhmm_time(time_str, time_type=""):
    if not time_str or not isinstance(time_str, str):
        raise UserError(f"Invalid {time_type} time format. Must be a string in HHMM format.")

    time_str = time_str.zfill(4)
    try:
        hours = int(time_str[:2])
        minutes = int(time_str[2:])
    except ValueError:
        raise UserError(f"Invalid {time_type} time format. Expected HHMM digits.")

    if not (0 <= hours <= 23 and 0 <= minutes <= 59):
        raise UserError(f"Invalid {time_type} time value. Must be between 0000 and 2359.")

    return datetime.datetime.combine(datetime.date.today(), datetime.time(hour=hours, minute=minutes))

def calculate_duration(start_dt, end_dt):
    return (end_dt - start_dt).total_seconds() / 3600.0

def is_overlap(start1, end1, start2, end2):
    return start1 < end2 and end1 > start2

def get_today():
    return datetime.date.today()

def get_yesterday():
    return get_today() - datetime.timedelta(days=1)

def get_thirty_days_ago():
    return get_today() - datetime.timedelta(days=30)
