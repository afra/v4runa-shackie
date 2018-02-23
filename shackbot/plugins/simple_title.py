from urllib.parse import urlsplit

import requests
from bs4 import BeautifulSoup

from bot import Bot

bot = Bot()

def _handle_title(url, bot, target):
    try:
        domain = "{0.netloc}".format(urlsplit(url))

        response = requests.get(url, allow_redirects=True, timeout=2)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.string.strip()

        if title:
            title = title.split('\n')[0]
            title = title[:400] + '…' if len(title) > 400 else title
            bot.say(target, 'Title: {title} (at {domain})'.format(title=title, domain=domain))
    except:
        pass

@bot.on('message')
def title(parsed, user, target, text):
    if 'http://' in text or 'https://' in text:
        url = text[text.find('http'):].split()[0]
        _handle_title(url, bot, target)
