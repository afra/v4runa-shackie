import asyncio
import async_timeout
import aiohttp
from datetime import datetime

from bot import Bot
from registry import bot_command
from storage import store, get_float

from hbmqtt.client import MQTTClient, ClientException
from hbmqtt.mqtt.constants import QOS_2

try:
    from config import AFRA_TOKEN
except ImportError:
    AFRA_TOKEN = "foo"

_OPEN = 1
_CLOSED = 2
_UNKNOWN = 3

async def update_spaceapi(state):
    if state not in [_OPEN, _CLOSED]:
        # TODO: unknown states
        return

    state = 0 if state == _CLOSED else 1
    url = 'https://spaceapi.afra.fe80.eu/status/{}/{}'.format(AFRA_TOKEN, state)

    try:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            with async_timeout.timeout(5):
                async with session.put(url) as resp:
                    return await resp.text()
    except:
        return None

def say_state(state):
    human = {
        _OPEN: "open",
        _CLOSED: "close",
        _UNKNOWN: "unknown",
        }
    bot = Bot()
    bot.say("#afra", "The space is now %s" % human[state])

async def check_state_change():
    ts_state, _ = get_space()
    state = store.get('open')
    if str(ts_state) != str(state, 'utf-8'):
        await update_spaceapi(ts_state)
        store.set('open', ts_state)
        say_state(ts_state)

@asyncio.coroutine
async def wait_kick_space():
    """ called from an external trigger.
    will be called regular when the door is
    open"""

    while True:
        mqcli = MQTTClient()
        await mqcli.connect('mqtt://localhost/')
        await mqcli.subscribe([
            ('afra/door', QOS_2),
            ])
        await mqcli.deliver_message()
        # TODO: ignoring the payload for now
        store.set('door_kicked_timestamp', datetime.now().timestamp())
        await check_state_change()

def set_space(state):
    # seconds ince epoch
    if state == _OPEN:
        store.set('door_irc_open_timestamp', datetime.now().timestamp())
    else:
        store.set('door_irc_closed_timestamp', datetime.now().timestamp())

def get_space():
    irc_open = get_float('door_irc_open_timestamp')
    irc_closed = get_float('door_irc_closed_timestamp')
    kicked = get_float('door_kicked_timestamp')

    if not irc_open and not irc_closed and not kicked:
        return (_UNKNOWN, '0.0')

    now = datetime.now().timestamp()
    if (irc_closed + 20 * 60) > now:
        #                20 min
        return (_CLOSED, irc_closed)
    elif (irc_open + 4 * 60 * 60) > now:
        #                   4 h
        return (_OPEN, irc_open)
    elif (kicked + 15 * 60) > now:
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
async def open_set(parsed, user, target, text):
    bot = Bot()
    set_space(_OPEN)
    await check_state_change()
    bot.say(target, "Noted.")

@bot_command('closed!')
async def closed_set(parsed, user, target, text):
    bot = Bot()
    set_space(_CLOSED)
    await check_state_change()
    bot.say(target, "Noted.")

asyncio.ensure_future(wait_kick_space())
