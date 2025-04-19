# Gets Dictionary.com's word of the day & definition
# Overlays word & definition over wallpaper in folder
# Saves file
# Sets file as desktop wallpaper

import ctypes
import os
import re

import requests

from .html_converter import html_to_text
from .image_generation import WallpaperImage


def get_wotd() -> dict:
    """
    applies regex to Dictionary.com word of the day page to return data
    :return: [word, type, definition, pronunciation]
    """

    wotd_link = "https://www.dictionary.com/e/word-of-the-day/"
    wotd_filter = r"\d{2}\, \d{4} (.*)\s\[(.*)\]\s\[(.*)\]\s.*\s*(.*)\s*(.*)"

    res = requests.get(wotd_link)
    res.raise_for_status()
    re.compile(wotd_filter, re.DOTALL)
    text = html_to_text(res.text)

    match = re.search(wotd_filter, text)
    wotd_dict = dict()
    if match:
        # print(match.groups()) # debug
        word = match.group(1).capitalize().strip()
        pronunciation = match.group(2).strip()
        type = match.group(4).strip()
        definition = match.group(5).strip()
        # definitions = definitions.strip().split(" (")
        # definition = definitions[0]

        wotd_dict = {
            "word": word,
            "type": type,
            "pronunciation": pronunciation,
            "definition": definition,
        }
        print(wotd_dict)
    else:
        print("Error: no word obtained.")
    return wotd_dict


def set_wallpaper(file: str):
    """
    set Windows desktop wallpaper to specified file
    :param file: file to set as desktop wallpaper
    """
    f = os.path.abspath(file)
    SPI_SETDESKTOPWALLPAPER = 20
    ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKTOPWALLPAPER, 0, f, 3
    )


if __name__ == "__main__":
    wotd = get_wotd()
    bg = WallpaperImage(
        wotd=wotd,
        output_filename="wotd_wallpaper.png",
    ).run()
    set_wallpaper(bg)
