# FILE: knowme/utils.py

import datetime

def colorize(text, color="orange"):
    """
    Colorizes text using ANSI escape codes.
    """
    colors = {
        "orange": "38;5;208",
        "red": "31",
        "green": "32",
        "yellow": "33",
    }
    color_code = colors.get(color, colors["orange"])
    return f"\033[{color_code}m{text}\033[0m"

def format_bytes(byte_count):
    """
    Formats a byte count into a human-readable string (KB, MB, GB, etc.).
    """
    if byte_count is None:
        return "N/A"
    power = 1024
    n = 0
    power_labels = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while byte_count >= power and n < len(power_labels):
        byte_count /= power
        n += 1
    return f"{byte_count:.2f} {power_labels[n]}B"

def format_uptime(seconds):
    """
    Formats a duration in seconds into a human-readable string (days, hours, minutes).
    """
    delta = datetime.timedelta(seconds=seconds)
    days = delta.days
    hours, rem = divmod(delta.seconds, 3600)
    minutes, _ = divmod(rem, 60)
    
    uptime_str = ""
    if days > 0:
        uptime_str += f"{days} days, "
    if hours > 0:
        uptime_str += f"{hours} hours, "
    uptime_str += f"{minutes} mins"
    
    return uptime_str