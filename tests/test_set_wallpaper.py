from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

from src.set_wallpaper import (
    _gsettings_set,
    _set_wallpaper_linux,
    _set_wallpaper_macos,
    _set_wallpaper_windows,
    set_wallpaper,
)

ABS_PATH = "/home/niall/wotd_wallpaper.png"
ABS_URI = Path(ABS_PATH).as_uri()


class TestSetWallpaperDispatch:
    """Tests that set_wallpaper dispatches to the correct platform handler."""

    @patch("src.set_wallpaper._set_wallpaper_windows")
    @patch("src.set_wallpaper.platform.system", return_value="Windows")
    def test_dispatches_to_windows(self, _mock_system, mock_windows):
        """Dispatches to Windows handler on Windows."""
        set_wallpaper(ABS_PATH)
        mock_windows.assert_called_once_with(ABS_PATH)

    @patch("src.set_wallpaper._set_wallpaper_linux")
    @patch("src.set_wallpaper.platform.system", return_value="Linux")
    def test_dispatches_to_linux(self, _mock_system, mock_linux):
        """Dispatches to Linux handler on Linux."""
        set_wallpaper(ABS_PATH)
        mock_linux.assert_called_once_with(ABS_PATH)

    @patch("src.set_wallpaper._set_wallpaper_macos")
    @patch("src.set_wallpaper.platform.system", return_value="Darwin")
    def test_dispatches_to_macos(self, _mock_system, mock_macos):
        """Dispatches to macOS handler on Darwin."""
        set_wallpaper(ABS_PATH)
        mock_macos.assert_called_once_with(ABS_PATH)

    @patch("src.set_wallpaper.platform.system", return_value="FreeBSD")
    def test_raises_on_unsupported_os(self, _mock_system):
        """Raises RuntimeError for unsupported operating systems."""
        with pytest.raises(RuntimeError, match="Unsupported operating system"):
            set_wallpaper(ABS_PATH)


class TestSetWallpaperWindows:
    """Tests for the Windows wallpaper setter."""

    def test_calls_system_parameters_info(self):
        """Calls SystemParametersInfoW with the correct arguments."""
        mock_windll = MagicMock()
        with patch("src.set_wallpaper.ctypes.windll", mock_windll, create=True):
            _set_wallpaper_windows(ABS_PATH)
        mock_windll.user32.SystemParametersInfoW.assert_called_once_with(20, 0, ABS_PATH, 3)


class TestSetWallpaperLinux:
    """Tests for the Linux wallpaper setter."""

    @patch("src.set_wallpaper._gsettings_set")
    def test_cinnamon_via_xdg(self, mock_gs):
        """Uses Cinnamon schema when XDG_CURRENT_DESKTOP is X-Cinnamon."""
        with patch.dict("os.environ", {"XDG_CURRENT_DESKTOP": "X-Cinnamon", "DESKTOP_SESSION": ""}):
            _set_wallpaper_linux(ABS_PATH)
        mock_gs.assert_called_once_with("org.cinnamon.desktop.background", "picture-uri", ABS_URI)

    @patch("src.set_wallpaper._gsettings_set")
    def test_cinnamon_via_session(self, mock_gs):
        """Uses Cinnamon schema when DESKTOP_SESSION contains cinnamon."""
        with patch.dict("os.environ", {"XDG_CURRENT_DESKTOP": "", "DESKTOP_SESSION": "cinnamon"}):
            _set_wallpaper_linux(ABS_PATH)
        mock_gs.assert_called_once_with("org.cinnamon.desktop.background", "picture-uri", ABS_URI)

    @patch("src.set_wallpaper._gsettings_set")
    def test_gnome(self, mock_gs):
        """Uses GNOME schema when XDG_CURRENT_DESKTOP is GNOME."""
        with patch.dict("os.environ", {"XDG_CURRENT_DESKTOP": "GNOME", "DESKTOP_SESSION": ""}):
            _set_wallpaper_linux(ABS_PATH)
        mock_gs.assert_called_once_with("org.gnome.desktop.background", "picture-uri", ABS_URI)

    @patch("src.set_wallpaper._gsettings_set")
    def test_unity(self, mock_gs):
        """Uses GNOME schema when XDG_CURRENT_DESKTOP is Unity."""
        with patch.dict("os.environ", {"XDG_CURRENT_DESKTOP": "Unity", "DESKTOP_SESSION": ""}):
            _set_wallpaper_linux(ABS_PATH)
        mock_gs.assert_called_once_with("org.gnome.desktop.background", "picture-uri", ABS_URI)

    @patch("src.set_wallpaper._gsettings_set")
    def test_mate(self, mock_gs):
        """Uses MATE schema with file path (not URI) when desktop is MATE."""
        with patch.dict("os.environ", {"XDG_CURRENT_DESKTOP": "MATE", "DESKTOP_SESSION": ""}):
            _set_wallpaper_linux(ABS_PATH)
        mock_gs.assert_called_once_with("org.mate.background", "picture-filename", ABS_PATH)

    @patch("src.set_wallpaper._gsettings_set")
    def test_unknown_desktop_falls_back_to_gnome(self, mock_gs):
        """Falls back to GNOME schema and logs a warning for unknown desktops."""
        with patch.dict("os.environ", {"XDG_CURRENT_DESKTOP": "XFCE", "DESKTOP_SESSION": ""}):
            _set_wallpaper_linux(ABS_PATH)
        mock_gs.assert_called_once_with("org.gnome.desktop.background", "picture-uri", ABS_URI)


class TestGsettingsSet:
    """Tests for the gsettings subprocess wrapper."""

    @patch("src.set_wallpaper.subprocess.run")
    def test_runs_correct_command(self, mock_run):
        """Runs gsettings with the correct schema, key, and value."""
        _gsettings_set("org.gnome.desktop.background", "picture-uri", ABS_URI)
        mock_run.assert_called_once_with(
            ["gsettings", "set", "org.gnome.desktop.background", "picture-uri", ABS_URI],
            check=True,
        )


class TestSetWallpaperMacos:
    """Tests for the macOS wallpaper setter."""

    @patch("src.set_wallpaper.subprocess.run")
    def test_runs_osascript(self, mock_run):
        """Runs osascript with the correct AppleScript command."""
        _set_wallpaper_macos(ABS_PATH)
        expected_script = f'tell application "Finder" to set desktop picture to POSIX file "{ABS_PATH}"'
        mock_run.assert_called_once_with(["osascript", "-e", expected_script], check=True)
