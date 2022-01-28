import configparser
import os
import textwrap

from PIL import Image, ImageDraw, ImageFont


def get_configs():
    """Retrieve all configuration parameters."""
    conf_files = ["wotd_wallpaper.conf", "user_configuration.conf"]
    if not os.path.exists("wotd_wallpaper.conf"):
        print("\nError: Can't find configuration file: wotd_wallpaper.conf")
    config = configparser.ConfigParser()
    config.read(conf_files, encoding="utf-8")
    return config


class WallpaperImage:
    def __init__(self, wotd: dict, output_filename: str):
        """
        :param  wotd: list of data [word, definition, pronunciation]
        :param  img:
        :param  config:
        :param  output_filename:
        """
        self.img = Image.open("base_wallpaper.png")
        self.config = get_configs()
        self.wotd_dict = wotd
        self.output_filename = output_filename

    def run(self) -> str:
        """
        create output image with text overlaid on background
        :return self.output_filename: filename of our image
        """
        wotd_dict = self.wotd_dict
        # only change the file if there's something to change it to
        if wotd_dict:
            # offset each section by height of previous text box
            current_offset = 0
            # add to image for each section in wotd dictionary
            for key in wotd_dict.keys():
                current_offset = self.write_msg(
                    wotd_dict[key], key, current_offset
                )
            self.img.save(self.output_filename)
        return self.output_filename

    def write_msg(
        self, msg: str, conf_section: str, current_offset: float
    ) -> float:
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
        font = self.config.get(conf_section, "Font")
        font_size = self.get_conf_int(conf_section, "Size")
        h_offset = self.get_conf_int(conf_section, "Horizontal offset")
        v_offset = self.get_conf_int(conf_section, "Vertical offset")
        colour = self.fix_colour_string(
            self.config.get(conf_section, "Colour")
        )

        if font_size > 0:
            font_obj = ImageFont.truetype(font, font_size)
            W, H = self.img.size
            w, h = font_obj.getsize(msg)
            ascent, descent = font_obj.getmetrics()
            h = ascent + descent + v_offset

            if current_offset == 0:
                current_offset = v_offset + ((H - h) / 2)

            # wrap string if it's too long
            if w >= (0.95 * W):
                self.wrap_string(msg, conf_section, current_offset)
                return 0
            pos = (((W - w) / 2) + h_offset, current_offset)

            draw = ImageDraw.Draw(self.img)
            draw.text(pos, msg, colour, font_obj)
            # draw.rectangle(
            #     [pos, (pos[0] + w, pos[1] + h)],
            #     fill=None,
            #     outline=(255, 255, 255),
            # )  # debug
            current_offset += h

        return current_offset

    def get_conf_int(self, section, param):
        """
        get integer from named config section for named param
        :param  section: section name in self.config
        :param  param: parameter in self.config
        :return integer: integer corresponding to param entry
        """
        integer = 0
        str_param = self.config.get(section, param)
        if str_param.replace(" ", "") != "":
            integer = self.config.getint(section, param)
        return integer

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

    def wrap_string(self, msg, conf_section, current_offset):
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
            v = (index * line_space) + current_offset
            self.write_msg(line, conf_section, v)
        return
