import ctypes
import logging
import os
import platform
import subprocess
from pathlib import Path

LOGGER = logging.getLogger(__name__)


def set_wallpaper(file: str) -> None:
    """
    Set the desktop wallpaper to the specified file, detecting the current OS.

    :param file: path to the image file to set as wallpaper
    """
    abs_path = os.path.abspath(file)
    system = platform.system()
    if system == "Windows":
        _set_wallpaper_windows(abs_path)
    elif system == "Linux":
        _set_wallpaper_linux(abs_path)
    elif system == "Darwin":
        _set_wallpaper_macos(abs_path)
    else:
        raise RuntimeError(f"Unsupported operating system: {system}")


def _set_wallpaper_windows(path: str) -> None:
    """
    Set the desktop wallpaper on Windows using the SystemParametersInfoW API.

    :param path: absolute path to the image file
    """
    SPI_SETDESKTOPWALLPAPER = 20
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKTOPWALLPAPER, 0, path, 3)


def _set_wallpaper_linux(path: str) -> None:
    """
    Set the desktop wallpaper on Linux via gsettings, selecting the correct schema
    based on the running desktop environment.

    :param path: absolute path to the image file
    """
    uri = Path(path).as_uri()
    desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
    session = os.environ.get("DESKTOP_SESSION", "").lower()

    if "cinnamon" in desktop or "cinnamon" in session:
        _gsettings_set("org.cinnamon.desktop.background", "picture-uri", uri)
    elif any(de in desktop for de in ("gnome", "unity", "budgie")):
        _gsettings_set("org.gnome.desktop.background", "picture-uri", uri)
    elif "mate" in desktop or "mate" in session:
        _gsettings_set("org.mate.background", "picture-filename", path)
    else:
        LOGGER.warning(
            "unrecognised desktop environment '%s'; falling back to GNOME schema",
            desktop or session or "unknown",
        )
        _gsettings_set("org.gnome.desktop.background", "picture-uri", uri)


def _gsettings_set(schema: str, key: str, value: str) -> None:
    """
    Run a gsettings set command.

    :param schema: GSettings schema (e.g. org.gnome.desktop.background)
    :param key: key within the schema
    :param value: value to set
    """
    subprocess.run(["gsettings", "set", schema, key, value], check=True)


def _set_wallpaper_macos(path: str) -> None:
    """
    Set the desktop wallpaper on macOS via osascript.

    :param path: absolute path to the image file
    """
    script = f'tell application "Finder" to set desktop picture to POSIX file "{path}"'
    subprocess.run(["osascript", "-e", script], check=True)
