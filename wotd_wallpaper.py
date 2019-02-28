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
import configparser

from html.parser import HTMLParser
from html.entities import name2codepoint


wotd_link = "https://www.dictionary.com/e/word-of-the-day/"
wotd_filter = r"\d{4}\s(\w*).*\[(.*)\](.*) See Full Definition"
fonts = [
    "LibreBaskerville-Regular.ttf",
    "LibreBaskerville-Regular.ttf"
]
base = "base_wallpaper.png"
output_filename = "wotd_wallpaper.png"


class _HTMLToText(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self._buf = []
        self.hide_output = False

    def handle_starttag(self, tag, attrs):
        if tag in ("p", "br") and not self.hide_output:
            self._buf.append("\n")
        elif tag in ("script", "style"):
            self.hide_output = True

    def handle_startendtag(self, tag, attrs):
        if tag == "br":
            self._buf.append("\n")

    def handle_endtag(self, tag):
        if tag == "p":
            self._buf.append("\n")
        elif tag in ("script", "style"):
            self.hide_output = False

    def handle_data(self, text):
        if text and not self.hide_output:
            self._buf.append(re.sub(r"\s+", " ", text))

    def handle_entityref(self, name):
        if name in name2codepoint and not self.hide_output:
            c = chr(name2codepoint[name])
            self._buf.append(c)

    def handle_charref(self, name):
        if not self.hide_output:
            n = int(name[1:], 16) if name.startswith("x") else int(name)
            self._buf.append(chr(n))

    def get_text(self):
        return re.sub(r" +", " ", "".join(self._buf))


def get_configs():
    """ Retrieve all configuration parameters."""
    conf_files = ["wotd_wallpaper.conf", "user_configuration.conf"]
    if not os.path.exists("wotd_wallpaper.conf"):
        print("\nError: Can't find configuration file: wotd_wallpaper.conf")
    config = configparser.ConfigParser()
    config.read(conf_files, encoding="utf-8")
    return config


def html_to_text(html):
    # from https://gist.github.com/Crazometer/af441bc7dc7353d41390a59f20f07b51
    """
    Given a piece of HTML, return the plain text it contains.
    This handles entities and char refs, but not javascript and stylesheets.
    """
    parser = _HTMLToText()
    parser.feed(html)
    parser.close()
    return parser.get_text()
    
def fix_encoding(str):
    """
    fix character encoding for proper output
    :param str: string to be converted
    :return str: utf8-encoded string
    """
    b = str.encode("latin1")  # convert from mistaken latin1 encoding
    str = b.decode("utf8")  # convert from bytes to utf-8
    return str


def get_wotd():
    """
    applies regex to dictionary.com word of the day page to return data
    :return: [word, definition, pronunciation]
    """
    res = requests.get(wotd_link)
    res.raise_for_status()
    regex = re.compile(wotd_filter)
    text = html_to_text(res.text)
    match = regex.search(text)

    if match:
        word = match.group(1).capitalize().strip()
        pronunciation = match.group(2).strip()
        definition = match.group(3).strip()
        print("{} ({}): {}".format(word, pronunciation, definition))
        return [word, definition, pronunciation]
    else:
        print("Error: no word obtained.")
        return []


def set_wallpaper(file):
    """
    set windows desktop wallpaper to specified file
    :param file: file to set as desktop wallpaper
    """
    f = os.path.abspath(file)
    SPI_SETDESKTOPWALLPAPER = 20
    ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKTOPWALLPAPER, 0, f, 3)
    return
    
class WallpaperImage:
    def __init__(self, config_object, wotd, filename):
        """
        :param  wotd: list of data [word, definition, pronunciation]
        :param  img:
        :param  config:
        :param  output_filename:
        """
        self.img = Image.open(base)
        self.config = config_object
        self.wotd = wotd
        self.output_filename = filename
    
    def run(self):
        """
        create output image with text overlaid on background
        :return self.output_filename: filename of our image
        """
        wotd = self.wotd
        # only change the file if there's something to change it to
        if wotd:
            sections = ["word", "definition"]  # can add more sections if needed
            size = [0, 0]  # offset each section by size of previous text box
            for index, section in enumerate(sections):
                size = self.write_msg(wotd[index], section, size)
            self.img.save(self.output_filename)
        return self.output_filename


    def write_msg(self, msg, conf_section, size):
        """
        write a line of text on the image according to specified parameters
        :param msg: text to write
        :param conf_section: string name of section in config object to use
        :param font: font to use
        :param font_size: font size
        :param h_offset: horizontal offset of text box from centre of image
        :param v_offset: vertical offset of text box from centre of image
        :return [w, h]: width and height of text box
        """
        msg = fix_encoding(msg)
        font = self.config.get(conf_section, "Font")
        font_size = self.config.getint(conf_section, "Size")
        h_offset = self.config.getint(conf_section, "Horizontal offset")
        v_offset = self.config.getint(conf_section, "Vertical offset") + size[1]
        colour = self.fix_colour_string(config.get(conf_section, "Colour"))

        font_obj = ImageFont.truetype(font, font_size)
        W, H = self.img.size
        w, h = font_obj.getsize(msg)
        # wrap string if it's too long
        if w >= W:
            wrap_string(msg, font, font_size, h_offset, v_offset)
            return
        pos = (((W-w)/2) + h_offset, ((H-h)/2) + v_offset)
        
        draw = ImageDraw.Draw(self.img)
        draw.text(pos, msg, colour, font_obj)
        return [w, h]
        
    def fix_colour_string(self, str):
        """
        converts string of "(255, 255, 255)" into tuple of same
        :param str: string version of tuple
        :return col: usable colour tuple
        """
        str = str.replace("(", "")
        str = str.replace(")", "")
        str = str.replace(" ", "")
        string_list = str.split(",")
        col = (int(string_list[0]), int(string_list[1]), int(string_list[2]))
        return col

    def wrap_string(self, msg, font, font_size, h_offset, v_offset):
        """
        split message into lines and wrap text if it's too wide
        :param msg: text to write
        :param font: font to use
        :param font_size: font size
        :param h_offset: horizontal offset of text box from centre of image
        :param v_offset: vertical offset of text box from centre of image
        """
        wrapped_list = textwrap.wrap(msg, 100)
        line_space = 60
        for index, line in enumerate(wrapped_list):
            h = h_offset
            v = (index * line_space) + v_offset
            write_msg(line, font, font_size, h, v)
        return


config = get_configs()
wotd = get_wotd()
bg = WallpaperImage(config, wotd, output_filename).run()
set_wallpaper(bg)
