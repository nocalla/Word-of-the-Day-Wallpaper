import ctypes
import logging
import os
import platform
import shutil
import subprocess
import time
from pathlib import Path

LOGGER = logging.getLogger(__name__)


def set_wallpaper(file: str) -> None:
    """
    Set the desktop wallpaper to the specified file, detecting the current OS.

    Desktops cache wallpapers by path and ignore an image regenerated in place, so the
    image is applied via a uniquely named copy; copies from earlier runs are removed.

    :param file: path to the image file to set as wallpaper
    """
    abs_path = Path(os.path.abspath(file))
    system = platform.system()
    setters = {
        "Windows": _set_wallpaper_windows,
        "Linux": _set_wallpaper_linux,
        "Darwin": _set_wallpaper_macos,
    }
    if system not in setters:
        raise RuntimeError(f"Unsupported operating system: {system}")

    unique = abs_path.with_name(f"{abs_path.stem}_{time.time_ns()}{abs_path.suffix}")
    shutil.copyfile(abs_path, unique)
    try:
        setters[system](str(unique))
    except Exception:
        unique.unlink(missing_ok=True)
        raise
    for old in abs_path.parent.glob(f"{abs_path.stem}_*{abs_path.suffix}"):
        if old != unique:
            old.unlink(missing_ok=True)


def _set_wallpaper_windows(path: str) -> None:
    """
    Set the desktop wallpaper on Windows using the SystemParametersInfoW API.

    :param path: absolute path to the image file
    """
    SPI_SETDESKTOPWALLPAPER = 20
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKTOPWALLPAPER, 0, path, 3)


def _set_wallpaper_linux(path: str) -> None:
    """
    Set the desktop wallpaper on Linux, using plasma-apply-wallpaperimage on KDE and
    gsettings (with the schema for the running desktop environment) otherwise.

    :param path: absolute path to the image file
    """
    uri = Path(path).as_uri()
    desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
    session = os.environ.get("DESKTOP_SESSION", "").lower()

    if "cinnamon" in desktop or "cinnamon" in session:
        _gsettings_set("org.cinnamon.desktop.background", "picture-uri", uri)
    elif any(de in desktop for de in ("gnome", "unity", "budgie")):
        _gsettings_set("org.gnome.desktop.background", "picture-uri", uri)
    elif "kde" in desktop or "plasma" in session:
        subprocess.run(["plasma-apply-wallpaperimage", path], check=True)
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
