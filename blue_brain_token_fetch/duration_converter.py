"""These functions allow to return any given duration of the form :
'{float > 0}{eventual unit of time (string)}' in seconds. Time units covered are :
seconds, minutes, hours and days.
"""
import re

m = 60
h = m * 60
d = h * 24


def convert_duration_to_sec(duration):
    """
    Take in input a duration (string) '{float > 0}{eventual unit of time}' and
    return its value in seconds.

    Parameters:
        duration : (string) of the form '{float > 0}{eventual unit of time}'.

    Returns:
        value in seconds of the input duration (float).
    """
    coefficient = 1
    re_expression = (
        r"^(-?(?:\d+)?\.?\d+) *(seconds?|secs?|s|minutes?|mins?|m|hours?|hrs?|h|days?"
        "|d|weeks?|w|years?|yrs?|y)?|d$"
    )

    match = re.match(re_expression, duration, re.M | re.I)

    if match:
        if match.group(2):
            coefficient = _convert_string_to_time_unit(match.group(2))
        if float(match.group(1)) > 0:
            return float(match.group(1)) * coefficient

        raise ValueError(
            "The number detected in the input duration need to be positive."
        )

    raise TypeError(
        f"Input duration '{duration}' is not of the form:\n'{{float > 0}}"
        "{{eventual unit of time}}'"
    )


def _convert_string_to_time_unit(time_unit):

    seconds = ["s", "sec", "secs", "second", "seconds"]
    minutes = ["m", "min", "mins", "minute", "minutes"]
    hours = ["h", "hr", "hrs", "hour", "hours"]
    days = ["d", "day", "days"]

    if time_unit in seconds:
        return 1
    elif time_unit in minutes:
        return m
    elif time_unit in hours:
        return h
    elif time_unit in days:
        return d
    else:
        raise ValueError(
            f"Input time_unit {time_unit} does not correspond to these time units : "
            "seconds, minutes, hours, days."
        )
