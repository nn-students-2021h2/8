from datetime import datetime


def pretty_print(unixtime):
    formatted_time = datetime.fromtimestamp(unixtime).strftime('%Y-%m-%d %H:%M:%S')
    return formatted_time
