from bot import Bot
from registry import bot_command
from storage import store

from datetime import datetime

_OPEN = 1
_CLOSED = 2
_UNKNOWN = 3

def set_space(state):
    store.set('open', state)
    # seconds ince epoch
    store.set('open_timestamp', datetime.now().timestamp())

def get_space():
    timestamp = store.get('open_timestamp')
    timestamp = str(timestamp, 'utf-8')
    timestamp = float(timestamp)
    timestamp = datetime.fromtimestamp(timestamp)
    timestamp = timestamp.ctime()
    state = store.get('open')
    state = int(state)
    return (state, timestamp)

@bot_command('open?')
def open_get(parsed, user, target, text):
    bot = Bot()
    status, timestamp = get_space()
    print(status, timestamp)

    if status == _CLOSED:
        bot.say(target, "The space is closed since {}".format(timestamp))
    elif status == _OPEN:
        bot.say(target, "The space is open since {}".format(timestamp))
    else:
        bot.say(target, "Who knows if the space is open or not")

@bot_command('open!')
def open_set(parsed, user, target, text):
    bot = Bot()
    set_space(_OPEN)
    bot.say(target, "Noted.")

@bot_command('closed!')
def open_set(parsed, user, target, text):
    bot = Bot()
    set_space(_CLOSED)
    bot.say(target, "Noted.")

