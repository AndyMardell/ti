# coding: utf-8

from __future__ import print_function
from __future__ import unicode_literals

import os
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta
from collections import defaultdict
from action import *
import yaml
import re
import colors


import time_store
from ti_exceptions import *


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


def parse_args(argv=sys.argv):
    global use_color

    if '--no-color' in argv:
        use_color = False
        argv.remove('--no-color')

    # prog = argv[0]
    if len(argv) == 1:
        raise BadArguments("You must specify a command.")

    head = argv[1]
    tail = argv[2:]

    if head in ['-h', '--help', 'h', 'help']:
        raise BadArguments()

    elif head in ['e', 'edit']:
        fn = action_edit
        args = {}

    elif head in ['o', 'on']:
        if not tail:
            raise BadArguments("Need the name of whatever you are working on.")

        fn = TiActionOn(colors.TiColorText(use_color))
        args = {
            'name': tail[0],
            'time': to_datetime(' '.join(tail[1:])),
        }

    elif head in ['f', 'fin']:
        fn = action_fin
        args = {'time': to_datetime(' '.join(tail))}

    elif head in ['s', 'status']:
        fn = action_status
        args = {}

    elif head in ['l', 'log']:
        fn = action_log
        args = {'period': tail[0] if tail else None}

    elif head in ['t', 'tag']:
        if not tail:
            raise BadArguments("Please provide at least one tag to add.")

        fn = action_tag
        args = {'tags': tail}

    elif head in ['n', 'note']:
        if not tail:
            raise BadArguments("Please provide some text to be noted.")

        fn = action_note
        args = {'content': ' '.join(tail)}

    elif head in ['i', 'interrupt']:
        if not tail:
            raise BadArguments("Need the name of whatever you are working on.")

        fn = action_interrupt
        args = {
            'name': tail[0],
            'time': to_datetime(' '.join(tail[1:])),
        }

    else:
        raise BadArguments("I don't understand %r" % (head,))

    return fn, args


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



store = time_store.JsonStore(os.getenv('SHEET_FILE', None) or
                  os.path.expanduser('~/.ti-sheet'))
use_color = True
