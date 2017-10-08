from datetime import datetime


def parse_isotime(isotime):
    return datetime.strptime(isotime, '%Y-%m-%dT%H:%M:%S.%fZ')