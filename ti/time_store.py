import json
from datetime import datetime
from utils import parse_isotime
import os


class JsonStore(object):
    def __init__(self, filename):
        self.filename = filename
        self.work_data = None
        self.interrupt_data = None

    def load(self):
        json_data = self.load_json()

        time_data = {'work': [], 'interrupt_stack': []}
        for log in json_data["work"]:
            time_data["work"].append(TimeLog(log, self))

        for log in json_data["interrupt_stack"]:
            time_data["interrupt_stack"].append(TimeLog(log, self))

        self.work_data = time_data["work"]
        self.interrupt_data = time_data["interrupt_stack"]
        return time_data

    def dump(self):
        json_data = {'work': [], 'interrupt_stack': []}
        for log in self.work_data:
            json_data["work"].append(log.json_item)

        for log in self.interrupt_data:
            json_data["interrupt_stack"].append(log.json_item)

        self.dump_json(json_data)

    def dump_json(self, json_data):
        with open(self.filename, 'w') as f:
            json.dump(json_data, f, separators=(',', ': '), indent=2)

    def load_json(self):
        if os.path.exists(self.filename):
            with open(self.filename) as f:
                json_data = json.load(f)
        else:
            json_data = {'work': [], 'interrupt_stack': []}

        return json_data

    def start_work(self, name, time):
        entry = {
            'name': name,
            'start': time,
        }
        self.work_data.append(TimeLog(entry, self))
        self.dump()

    def end_work(self, time):
        current = self.work_data[-1]
        current.json_item["end"] = time
        self.dump()

    def add_interruption(self):
        interrupted = self.work_data[-1]
        self.interrupt_data.append(interrupted)
        self.dump()

    def get_current_item(self):
        current = self.work_data[-1]
        return current


class TimeLog(object):
    def __init__(self, json_item, store):
        self.json_item = json_item
        self.store = store

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

    def add_note(self, content):
        if 'notes' not in self.json_item:
            self.json_item['notes'] = [content]
        else:
            self.json_item['notes'].append(content)

        self.store.dump()

    def add_tags(self, tags):
        self.json_item['tags'] = set(self.json_item.get('tags') or [])
        self.json_item['tags'].update(tags)
        self.json_item['tags'] = list(self.json_item['tags'])
        self.store.dump()
