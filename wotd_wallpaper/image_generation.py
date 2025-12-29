import configparser
import textwrap
from dataclasses import InitVar, dataclass, fields

from config_functions import fix_colour_string, get_conf_int
from get_wotd import WordOfTheDay
from PIL import Image, ImageDraw, ImageFont


def generate_image(
    wotd: WordOfTheDay,
    output_filename: str,
    base_image_path: str,
    config: configparser.ConfigParser,
) -> str:
    """
    generate wallpaper image with word of the day text overlaid
    :param wotd: WordOfTheDay dataclass object with word data
    :param output_filename: filename to save generated image as
    :param base_image_path: path to base image to overlay text on
    :return: path to generated image
    """
    img = Image.open(base_image_path)
    # offset each section by height of previous text box
    current_offset = 0
    # add to image for each section in wotd object
    for parameter in fields(wotd):
        Format = FieldFormat(config=config, section=parameter.name)
        current_offset = write_text_to_image(
            img,
            msg=getattr(wotd, parameter.name),
            current_offset=current_offset,
            Format=Format,
        )
    img.save(output_filename)
    return output_filename


@dataclass
class FieldFormat:
    """
    Dataclass to hold formatting parameters for each field in the WordOfTheDay dataclass.
    :param config: configparser object with configuration data
    :param section: section name in config corresponding to field
    """

    config: InitVar[configparser.ConfigParser]
    section: InitVar[str] = ""

    def __post_init__(self, config, section) -> None:
        """
        Initialize the FieldFormat object.

        :param config: configparser object with configuration data
        :type config: configparser.ConfigParser
        :param section: section name in config corresponding to field
        :type section: str
        """
        self.wotd_parameter = section
        self.font = config.get(section, "Font")
        self.font_size = get_conf_int(config, section, "Size")
        self.h_offset = get_conf_int(config, section, "Horizontal offset")
        self.v_offset = get_conf_int(config, section, "Vertical offset")
        self.colour = fix_colour_string(config.get(section, "Colour"))


def write_text_to_image(
    img, msg: str, Format: FieldFormat, current_offset: float
) -> float:
    """
    write a line of text on the image according to specified parameters
    :param msg: text to write
    :param Format: FieldFormat object with formatting parameters
    :param current_offset: current vertical offset from top of image
    :return [w, h]: width and height of text box
    """

    if Format.font_size > 0:
        font_obj = ImageFont.truetype(Format.font, Format.font_size)
        W, H = img.size
        text_bb = font_obj.getbbox(msg)
        w = text_bb[2] - text_bb[0]
        h = text_bb[3] - text_bb[1]
        ascent, descent = font_obj.getmetrics()
        h = ascent + descent + Format.v_offset

        if current_offset == 0:
            current_offset = Format.v_offset + ((H - h) / 2)

        # wrap string if it's too long
        if w >= (0.95 * W):
            wrap_string(img, msg, Format, current_offset)
            return 0
        pos = (((W - w) / 2) + Format.h_offset, current_offset)

        draw = ImageDraw.Draw(img)
        draw.text(pos, msg, Format.colour, font_obj)
        # draw.rectangle(
        #     [pos, (pos[0] + w, pos[1] + h)],
        #     fill=None,
        #     outline=(255, 255, 255),
        # )  # debug
        current_offset += h

    return current_offset


def wrap_string(img, msg: str, Format: FieldFormat, current_offset) -> None:
    """
    split message into lines and wrap text if it's too wide
    :param msg: text to write
    :param Format: FieldFormat object with formatting parameters
    :param current_offset: current vertical offset from top of image
    :return: None
    """
    wrapped_list = textwrap.wrap(msg, 100)
    line_space = 60
    for index, line in enumerate(wrapped_list):
        v = (index * line_space) + current_offset
        write_text_to_image(img, line, Format, v)
    return
