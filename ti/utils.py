from datetime import datetime, timedelta

import re

from ti_exceptions import *


def parse_isotime(isotime):
    return datetime.strptime(isotime, '%Y-%m-%dT%H:%M:%S.%fZ')


def timegap(start_time, end_time):
    diff = end_time - start_time

    mins = diff.total_seconds() / 60

    if mins == 0:
        return 'less than a minute'
    elif mins == 1:
        return 'a minute'
    elif mins < 44:
        return '{} minutes'.format(mins)
    elif mins < 89:
        return 'about an hour'
    elif mins < 1439:
        return 'about {} hours'.format(mins / 60)
    elif mins < 2519:
        return 'about a day'
    elif mins < 43199:
        return 'about {} days'.format(mins / 1440)
    elif mins < 86399:
        return 'about a month'
    elif mins < 525599:
        return 'about {} months'.format(mins / 43200)
    else:
        return 'more than a year'


def format_duration(duration):
    tmsg = []

    # Needs to be refactored
    if duration > 3600:
        hours = int(duration / 3600)
        duration -= hours * 3600
        tmsg.append(str(hours) + ' hour' + ('s' if hours > 1 else ''))

    if duration > 60:
        mins = int(duration / 60)
        duration -= mins * 60
        tmsg.append(str(mins) + ' minute' + ('s' if mins > 1 else ''))

    if duration:
        tmsg.append(str(duration) + ' second' + ('s' if duration > 1 else ''))

    return ', '.join(tmsg)[::-1].replace(',', '& ', 1)[::-1]


def to_datetime(timestr):
    return parse_engtime(timestr).isoformat() + 'Z'


def parse_engtime(timestr):

    now = datetime.utcnow()
    if not timestr or timestr.strip() == 'now':
        return now

    match = re.match(r'(\d+|a) \s* (s|secs?|seconds?) \s+ ago $',
                     timestr, re.X)
    if match is not None:
        n = match.group(1)
        seconds = 1 if n == 'a' else int(n)
        return now - timedelta(seconds=seconds)

    match = re.match(r'(\d+|a) \s* (mins?|minutes?) \s+ ago $', timestr, re.X)
    if match is not None:
        n = match.group(1)
        minutes = 1 if n == 'a' else int(n)
        return now - timedelta(minutes=minutes)

    match = re.match(r'(\d+|a|an) \s* (hrs?|hours?) \s+ ago $', timestr, re.X)
    if match is not None:
        n = match.group(1)
        hours = 1 if n in ['a', 'an'] else int(n)
        return now - timedelta(hours=hours)

    raise BadTime("Don't understand the time %r" % (timestr,))
