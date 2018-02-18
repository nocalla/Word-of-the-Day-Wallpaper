# wotd_wallpaper.py

# Gets Dictionary.com's word of the day & definition
# Overlays word & definition over wallpaper in folder
# Saves file
# Sets file as desktop wallpaper

#######################################################
from PIL import Image, ImageFont, ImageDraw
import os
import re
import requests
import ctypes
import textwrap

from html.parser import HTMLParser


wotd_link = "http://www.dictionary.com/wordoftheday"
wotd_filter = "Definitions for (\w*)\s(.*)"
fonts = ["Penshurs.ttf", "georgia.ttf"]
base = "base_wallpaper.png"
output_filename = "wotd_wallpaper.png"


class _HTMLToText(HTMLParser):
    # from https://gist.github.com/Crazometer/af441bc7dc7353d41390a59f20f07b51
    def __init__(self):
        HTMLParser.__init__(self)
        self._buf = []
        self.hide_output = False

    def handle_starttag(self, tag, attrs):
        if tag in ('p', 'br') and not self.hide_output:
            self._buf.append('\n')
        elif tag in ('script', 'style'):
            self.hide_output = True

    def handle_startendtag(self, tag, attrs):
        if tag == 'br':
            self._buf.append('\n')

    def handle_endtag(self, tag):
        if tag == 'p':
            self._buf.append('\n')
        elif tag in ('script', 'style'):
            self.hide_output = False

    def handle_data(self, text):
        if text and not self.hide_output:
            self._buf.append(re.sub(r'\s+', ' ', text))

    def handle_entityref(self, name):
        if name in name2codepoint and not self.hide_output:
            c = chr(name2codepoint[name])
            self._buf.append(c)

    def handle_charref(self, name):
        if not self.hide_output:
            n = int(name[1:], 16) if name.startswith('x') else int(name)
            self._buf.append(chr(n))

    def get_text(self):
        return re.sub(r' +', ' ', ''.join(self._buf))


def html_to_text(html):
    """
    Given a piece of HTML, return the plain text it contains.
    This handles entities and char refs, but not javascript and stylesheets.
    """
    parser = _HTMLToText()
    try:
        parser.feed(html)
        parser.close()
    except:  #HTMLParseError: No good replacement?
        pass
    return parser.get_text()


def get_wotd():
    # uses regular expressions to parse dictionary.com input
    res = requests.get(wotd_link)
    res.raise_for_status()
    regex = re.compile(wotd_filter)
    text = html_to_text(res.text)
    match = regex.search(text)
    
    if match:
        word = match.group(1).capitalize().strip()
        definition = match.group(2).strip()
        print("\t{}:\n\t{}".format(word, definition))
        return [word, definition]


def print_wotd(wotd):
    file = output_filename
    # only change the file if there's something to change it to
    if wotd:
        size = write_msg(wotd[0], fonts[0], 300, 0, 40)
        # offset definition by size of word text box
        size = write_msg(wotd[1], fonts[1], 45, 0, 20 + size[1])
        img.save(file)
    return file


def write_msg(msg, font, font_size, h_offset, v_offset):
    msg = fix_encoding(msg)
    font_obj = ImageFont.truetype(font, font_size)
    colour = (255, 255, 255)
    W, H = img.size
    w, h = font_obj.getsize(msg)
    if w >= W:
        wrap_string(msg, font, font_size, h_offset, v_offset)
        return
    pos = (((W-w)/2) + h_offset, ((H-h)/2) + v_offset)
    draw.text(pos, msg, colour, font_obj)
    return [w, h]


def fix_encoding(str):
    # fix character encoding for proper output
    b = str.encode("latin1")  # convert from mistaken latin1 encoding
    str = b.decode("utf8")  # convert from bytes to utf-8
    return str


def wrap_string(msg, font, font_size, h_offset, v_offset):
    wrapped_list = textwrap.wrap(msg, 100)
    line_space = 60
    for index, line in enumerate(wrapped_list):
        h = h_offset
        v = (index * line_space) + v_offset
        write_msg(line, font, font_size, h, v)
    return


def set_wallpaper(file):
    # set windows desktop wallpaper to specified file
    f = os.path.abspath(file)
    SPI_SETDESKTOPWALLPAPER = 20
    ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKTOPWALLPAPER, 0, f, 3)
    return


img = Image.open(base)
draw = ImageDraw.Draw(img)
get_wotd() # debug
#bg = print_wotd(get_wotd())
#set_wallpaper(bg)
