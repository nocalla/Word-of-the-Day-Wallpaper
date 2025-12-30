import ctypes
import os


def set_wallpaper(file: str) -> None:
    """
    set Windows desktop wallpaper to specified file
    :param file: file to set as desktop wallpaper
    """
    f = os.path.abspath(file)
    SPI_SETDESKTOPWALLPAPER = 20
    ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKTOPWALLPAPER, 0, f, 3
    )
