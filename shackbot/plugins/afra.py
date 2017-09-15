from datetime import datetime

from bot import Bot
from registry import bot_command
from storage import store

_OPEN = 1
_CLOSED = 2
_UNKNOWN = 3

def kick_space():
    """ called from an external trigger.
    will be called regular when the door is
    open"""
    store.set('door_kicked_timestamp', datetime.now().timestamp())

def set_space(state):
    store.set('open', state)
    # seconds ince epoch
    if state == _OPEN:
        store.set('door_irc_open_timestamp', datetime.now().timestamp())
    else:
        store.set('door_irc_closed_timestamp', datetime.now().timestamp())

def get_float(store_name):
    value = store.get(store_name)
    if not value:
        return 0.0
    value = float(value)
    return value

def get_space():
    irc_open = get_float('door_irc_open_timestamp')
    irc_closed = get_float('door_irc_closed_timestamp')
    kicked = get_float('door_kicked_timestamp')

    if not irc_open and not irc_closed and not kicked:
        return _UNKNOWN

    now = datetime.now()
    if (irc_closed + 20 * 60) > now:
        #                20 min
        return (_CLOSED, irc_closed)
    elif (irc_open + 4 * 60 * 60) > now():
        #                   4 h
        return (_OPEN, irc_open)
    elif (kicked + 15 * 60) > now():
        #                 15 min
        return (_OPEN, kicked)
    else:
        stamp = irc_open
        if stamp < irc_closed:
            stamp = irc_closed
        if stamp < kicked:
            stamp = kicked
        return (_CLOSED, stamp)

@bot_command('open?')
def open_get(parsed, user, target, text):
    bot = Bot()
    status, timestamp = get_space()
    print(status, timestamp)

    if status == _CLOSED:
        bot.say(target, "The space is closed.")
    elif status == _OPEN:
        bot.say(target, "The space is open.")
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

if __name__ == '__main__':
    kicked()
