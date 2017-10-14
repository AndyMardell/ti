import time_store
from ti_exceptions import *
from colorama import Fore


class TiAction(object):
    def __init__(self, ti_colors):
        self.ti_colors = ti_colors

    def execute_action(self, ti_store, args):
        data = ti_store.load()
        work_data = data['work']
        interrupt_data = data['interrupt_stack']
        self._run(ti_store, work_data, interrupt_data, args)

    def _run(self, ti_store, work_data, interrupt_data, args):
        raise NotImplementedError

    def _verify_status(self, work_data, interrupt_data):
        raise NotImplementedError


class TiWorkingAction(TiAction):
    def _verify_status(self, work_data, interrupt_data):
        if work_data.get('work') and work_data['work'][-1].is_current():
            return
        raise NoTask("For all I know, you aren't working on anything. "
                     "I don't know what to do.\n"
                     "See `ti -h` to know how to start working.")


class TiNotWorkingAction(TiAction):
    def _verify_status(self, work_data, interrupt_data):
        if work_data and work_data[-1].is_current():
            raise AlreadyOn("You are already working on %s. Stop it or use a "
                            "different sheet." % self.ti_colors.color_string(Fore.YELLOW, work_data[-1].get_name()))


class TiActionOn(TiNotWorkingAction):
    def _run(self, store,  work_data, interrupt_data, args):
        entry = {
            'name': args["name"],
            'start': args["time"],
        }

        work_data.append(time_store.TimeLog(entry))
        store.dump(work_data, interrupt_data)

        print('Start working on ' + self.ti_colors.color_string(Fore.GREEN, args["name"]) + '.')


class TiActionFin(TiWorkingAction):
    def _run(self, store,  work_data, interrupt_data, args):

        current = work_data[-1]
        current.json_item["end"] = args["time"]
        print('So you stopped working on ' + self.ti_colors.color_string(Fore.RED, current.get_name()) + '.')

        if len(interrupt_data) > 0:
            name = interrupt_data.pop().get_name()
            action_on(name, args["time"])
            if len(interrupt_data) > 0:
                print('You are now %d deep in interrupts.'
                      % len(interrupt_data))
            else:
                print('Congrats, you\'re out of interrupts!')
        store.dump(work_data, interrupt_data)






def action_on(name, time):
    data = store.load()
    work = data['work']

    if work and work[-1].is_current():
        raise AlreadyOn("You are already working on %s. Stop it or use a "
                        "different sheet." % (yellow(work[-1].get_name()),))

    #TODO: work directly on timelog objects here
    entry = {
        'name': name,
        'start': time,
    }

    work.append(time_store.TimeLog(entry))
    store.dump(data)

    print('Start working on ' + color_string(Fore.GREEN, name) + '.')


def action_fin(time, back_from_interrupt=True):
    ensure_working()

    data = store.load()

    current = data['work'][-1]
    current.json_item["end"] = time
    store.dump(data)
    print('So you stopped working on ' + color_string(Fore.RED, current.get_name()) + '.')

    if back_from_interrupt and len(data['interrupt_stack']) > 0:
        name = data['interrupt_stack'].pop().get_name()
        store.dump(data)
        action_on(name, time)
        if len(data['interrupt_stack']) > 0:
            print('You are now %d deep in interrupts.'
                  % len(data['interrupt_stack']))
        else:
            print('Congrats, you\'re out of interrupts!')


def action_interrupt(name, time):
    ensure_working()

    action_fin(time, back_from_interrupt=False)

    data = store.load()
    if 'interrupt_stack' not in data:
        data['interrupt_stack'] = []
    interrupt_stack = data['interrupt_stack']

    interrupted = data['work'][-1]
    interrupt_stack.append(interrupted)
    store.dump(data)

    action_on('interrupt: ' + color_string(Fore.GREEN, name), time)
    print('You are now %d deep in interrupts.' % len(interrupt_stack))


def action_note(content):
    ensure_working()

    data = store.load()
    current = data['work'][-1]

    if 'notes' not in current:
        current['notes'] = [content]
    else:
        current['notes'].append(content)

    store.dump(data)

    print('Yep, noted to ' + color_string(Fore.YELLOW, current.get_name()) + '.')


def action_tag(tags):
    ensure_working()

    data = store.load()
    current = data['work'][-1]

    current['tags'] = set(current.get('tags') or [])
    current['tags'].update(tags)
    current['tags'] = list(current['tags'])

    store.dump(data)

    tag_count = len(tags)
    print("Okay, tagged current work with %d tag%s."
          % (tag_count, "s" if tag_count > 1 else ""))


def action_status():
    ensure_working()

    data = store.load()
    current = data['work'][-1]

    start_time = current.get_start()
    diff = timegap(start_time, datetime.utcnow())

    print('You have been working on {0} for {1}.'.format(
        color_string(Fore.GREEN, current.get_name()), diff))


def action_log(period):
    data = store.load()
    work = data['work'] + data['interrupt_stack']
    log = defaultdict(lambda: {'delta': timedelta()})
    current = None

    for item in work:
        log[item.get_name()]["delta"] = item.get_delta()
        if item.is_current():
            current = item.get_name()

    name_col_len = 0

    for name, item in log.items():
        name_col_len = max(name_col_len, len(strip_color(name)))

        secs = item['delta'].total_seconds()
        tmsg = []

        if secs > 3600:
            hours = int(secs / 3600)
            secs -= hours * 3600
            tmsg.append(str(hours) + ' hour' + ('s' if hours > 1 else ''))

        if secs > 60:
            mins = int(secs / 60)
            secs -= mins * 60
            tmsg.append(str(mins) + ' minute' + ('s' if mins > 1 else ''))

        if secs:
            tmsg.append(str(secs) + ' second' + ('s' if secs > 1 else ''))

        log[name]['tmsg'] = ', '.join(tmsg)[::-1].replace(',', '& ', 1)[::-1]

#    for name, item in sorted(log.items(), key=(lambda x: x[1]), reverse=True):
#        print(ljust_with_color(name, name_col_len), ' ∙∙ ', item['tmsg'],
#              end=' ← working\n' if current == name else '\n')


def action_edit():
    if "EDITOR" not in os.environ:
        raise NoEditor("Please set the 'EDITOR' environment variable")

    data = store.load()
    yml = yaml.safe_dump(data, default_flow_style=False, allow_unicode=True)

    cmd = os.getenv('EDITOR')
    fd, temp_path = tempfile.mkstemp(prefix='ti.')
    with open(temp_path, "r+") as f:
        f.write(yml.replace('\n- ', '\n\n- '))
        f.seek(0)
        subprocess.check_call(cmd + ' ' + temp_path, shell=True)
        yml = f.read()
        f.truncate()
        f.close

    os.close(fd)
    os.remove(temp_path)

    try:
        data = yaml.load(yml)
    except:
        raise InvalidYAML("Oops, that YAML doesn't appear to be valid!")

    store.dump(data)


def is_working():
    data = store.load()
    return data.get('work') and data['work'][-1].is_current()


def ensure_working():
    if is_working():
        return

    raise NoTask("For all I know, you aren't working on anything. "
                 "I don't know what to do.\n"
                 "See `ti -h` to know how to start working.")


