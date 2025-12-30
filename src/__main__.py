# Gets Dictionary.com's word of the day & definition
# Overlays word & definition over wallpaper in folder
# Saves file
# Sets file as desktop wallpaper

from config_functions import get_configs
from get_wotd import get_data, parse_wotd_data
from image_generation import generate_image
from set_wallpaper import set_wallpaper

WOTD_LINK = "https://www.dictionary.com/word-of-the-day/"
WOTD_FILTER = r"\d{2}\, \d{4} (.*)\s\[(.*)\]\s(.*)\s(.*)\s.*\s(.*)\s.*\s(.*)"
OUTPUT_PATH = "output/wotd_wallpaper.png"
BASE_IMAGE_PATH = "assets/base_wallpaper.png"


if __name__ == "__main__":
    config = get_configs()
    website_data = get_data(WOTD_LINK)
    wotd = parse_wotd_data(website_data, WOTD_FILTER)

    bg = generate_image(
        wotd=wotd,
        output_filename=OUTPUT_PATH,
        base_image_path=BASE_IMAGE_PATH,
        config=config,
    )
    set_wallpaper(bg)
