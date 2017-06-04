from errbot import BotPlugin, re_botcmd
import re
import bs4
import requests


class LinkParser(BotPlugin):
    """Parses links and extracts embedded information"""

    @re_botcmd(prefixed=False, flags=re.IGNORECASE, pattern='(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)')
    def url_match(self, msg, match):
        # skip if in groupchat to circumvent parsing loop
        if msg.is_group:
            if msg.frm.client == self.bot_config.CHATROOM_FN:
                return
        url = match.groups()[0]
        self.log.info('got url: {}'.format(url))
        for parser in [parse_noembed, parse_soup]:
            try:
                title = parser(url)
                return '[{}]'.format(title.strip())
            except:
                self.log.debug('parser {} failed'.format(parser))
                continue
        self.log.info('no info found for url {}!'.format(url))


def parse_noembed(url):
    r = requests.get('https://noembed.com/embed', params={'url': url}, verify=False)
    resp = r.json()
    if 'error' in resp.keys():
        raise UserWarning('noembed found nothing!')
    return resp['title'].strip()


def parse_soup(url):
    r = requests.get(url, verify=False, stream=True, timeout=2)
    if 'text/html' not in r.headers['content-type']:
        raise UserWarning('not an html file!')
    r.raw.decode_content = True
    content = r.raw.read(100000 + 1)
    title = bs4.BeautifulSoup(content, 'html.parser').title.string
    title = title.replace('\n', ' ').replace('\r', ' ').strip()
    return title
