from errbot import BotPlugin, botcmd, re_botcmd
import re
import bs4
import requests
from IPython import embed

class LinkParser(BotPlugin):
    """Parses links and extracts embedded information"""

    @re_botcmd(prefixed=False, flags=re.IGNORECASE, pattern='(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)')
    def url_match(self, msg, match):
        r = requests.get('https://noembed.com/embed', params={'url': match.groups()[0]}, verify=False)
        resp = r.json()
        if 'error' in resp.keys():
            r = requests.get(match.groups()[0], verify=False)
            title = bs4.BeautifulSoup(r.text, 'html.parser').title.string
        else:
            title = resp['title']
        return '[{}]'.format(title.strip())