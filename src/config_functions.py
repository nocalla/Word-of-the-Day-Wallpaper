import configparser
import os
from pathlib import Path


def get_configs() -> configparser.ConfigParser:
    """Retrieve all configuration parameters."""
    conf_files = ["wotd_wallpaper.conf", "user_configuration.conf"]
    if not os.path.exists("wotd_wallpaper.conf"):
        print("\nError: Can't find configuration file: wotd_wallpaper.conf")
    config = configparser.ConfigParser()
    config.read(conf_files, encoding="utf-8")
    return config


def get_conf_int(
    config: configparser.ConfigParser, section: str, param: str
) -> int:
    """
    get integer from named config section for named param
    :param  section: section name in config
    :param  param: parameter in config
    :return integer: integer corresponding to param entry
    """
    integer = 0
    str_param = config.get(section, param)
    if str_param.replace(" ", "") != "":
        integer = config.getint(section, param)
    return integer


def get_conf_font(
    config: configparser.ConfigParser, section: str, param: str
) -> Path:
    """
    get font path from named config section for named param
    :param  section: section name in config
    :param  param: parameter in config
    :return Path: Path to font file
    """
    font_path = Path()
    str_param = config.get(section, param)
    if str_param.replace(" ", "") != "":
        font_path = Path("assets", str_param)
    return font_path


def fix_colour_string(input: str) -> tuple[int, ...]:
    """
    converts string of "(255, 255, 255)" into tuple of same
    :param str: string version of tuple
    :return col: usable colour tuple
    """
    # remove non-alphanumeric characters except commas
    input = "".join([char for char in input if char.isdigit() or char == ","])
    # split by commas and convert to integers (clamp to 255 max)
    string_list = input.split(",")
    col = tuple(min(int(x), 255) for x in string_list[:3])
    if len(col) < 3:
        col = (0, 0, 0)  # default to black if invalid
    return col
