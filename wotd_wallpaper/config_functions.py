import configparser
import os


def get_configs() -> configparser.ConfigParser:
    """Retrieve all configuration parameters."""
    conf_files = ["wotd_wallpaper.conf", "user_configuration.conf"]
    if not os.path.exists("wotd_wallpaper.conf"):
        print("\nError: Can't find configuration file: wotd_wallpaper.conf")
    config = configparser.ConfigParser()
    config.read(conf_files, encoding="utf-8")
    return config


def get_conf_int(config, section, param) -> int:
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


def fix_colour_string(input: str | None) -> tuple[int, int, int]:
    """
    converts string of "(255, 255, 255)" into tuple of same
    :param str: string version of tuple
    :return col: usable colour tuple
    """
    if input is None:
        return (255, 255, 255)
    input = input.replace("(", "")
    input = input.replace(")", "")
    input = input.replace(" ", "")
    string_list = input.split(",")
    col = (int(string_list[0]), int(string_list[1]), int(string_list[2]))
    return col
