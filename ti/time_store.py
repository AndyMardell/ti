import json
from datetime import datetime
from utils import parse_isotime
import os

class JsonStore(object):

    def __init__(self, filename):
        self.filename = filename

    def load(self):

        if os.path.exists(self.filename):
            with open(self.filename) as f:
                json_data = json.load(f)

        else:
            json_data = {'work': [], 'interrupt_stack': []}

        time_data = {'work': [], 'interrupt_stack': []}
        for log in json_data["work"]:
            time_data["work"].append(TimeLog(log))

        for log in json_data["interrupt_stack"]:
            time_data["interrupt_stack"].append(TimeLog(log))

        return time_data

    def dump(self, data):
        json_data = {'work': [], 'interrupt_stack': []}
        for log in data["work"]:
            json_data["work"].append(log.json_item)

        for log in data["interrupt_stack"]:
            json_data["interrupt_stack"].append(log.json_item)

        with open(self.filename, 'w') as f:
            json.dump(json_data, f, separators=(',', ': '), indent=2)


class TimeLog(object):
    def __init__(self, json_item):
        self.json_item = json_item

    def get_name(self):
        return self.json_item["name"];

    def get_start(self):
        return parse_isotime(self.json_item["start"])

    def get_end(self):
        return parse_isotime(self.json_item["end"])

    def get_delta(self):
        if 'end' in self.json_item:
            return self.get_end() - self.get_start()
        else:
            return datetime.utcnow() - self.get_start()

    def is_current(self):
        if 'end' in self.json_item:
            return False
        else:
            return True
