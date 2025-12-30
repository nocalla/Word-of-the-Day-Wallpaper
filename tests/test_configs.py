import configparser

import pytest

from src.config_functions import fix_colour_string, get_conf_int


@pytest.fixture
def test_config() -> configparser.ConfigParser:
    """
    Fixture to provide a ConfigParser object for testing.
    """
    conf_files = ["test_config.conf"]
    config = configparser.ConfigParser()
    config.read(conf_files, encoding="utf-8")
    return config


# def test_get_configs_valid(test_config: configparser.ConfigParser) -> None:
#     """
#     Test that configuration file search and load creates a ConfigParser object with the correct format.
#     """
#     assert 1 == 2  # Placeholder for actual test implementation


# def test_get_configs_user_pref_overwrite(
#     test_config: configparser.ConfigParser,
# ) -> None:
#     """
#     Test that user preferences override default configurations.
#     """
#     assert 1 == 2  # Placeholder for actual test implementation


def test_get_conf_int_valid(test_config: configparser.ConfigParser) -> None:
    """
    Test retrieval of integer configuration parameters where valid integer.
    """
    expected_result = 300
    test_result = get_conf_int(test_config, "test_section", "Size")
    assert expected_result == test_result


# def test_get_conf_int_invalid(test_config: configparser.ConfigParser) -> None:
#     """
#     Test retrieval of integer configuration parameters where invalid integer.
#     """
#     assert 1 == 2  # Placeholder for actual test implementation


# def test_get_conf_font_valid(test_config: configparser.ConfigParser) -> None:
#     """
#     Test retrieval of font path configuration parameters where valid font path.
#     """
#     assert 1 == 2  # Placeholder for actual test implementation


def test_fix_colour_string_valid() -> None:
    """
    Test conversion of colour string to tuple.
    """
    input_str = "(255, 0, 128)"
    expected_output = (255, 0, 128)
    assert fix_colour_string(input_str) == expected_output


def test_fix_colour_string_invalid_chars() -> None:
    """
    Test conversion of invalid colour string to tuple.
    """
    input_str = "(255!, 0xx, 128]"
    expected_output = (255, 0, 128)
    assert fix_colour_string(input_str) == expected_output


def test_fix_colour_string_too_many_values() -> None:
    """
    Test conversion of invalid colour string to tuple.
    """
    input_str = "(255, 0, 128, 64)"
    expected_output = (255, 0, 128)
    assert fix_colour_string(input_str) == expected_output


def test_fix_colour_string_too_few_values() -> None:
    """
    Test conversion of invalid colour string to tuple.
    """
    input_str = "(255, 0)"
    expected_output = (0, 0, 0)
    assert fix_colour_string(input_str) == expected_output


def test_fix_colour_string_negative_values() -> None:
    """
    Test conversion of invalid colour string to tuple.
    """
    input_str = "(-255, 0, 128)"
    expected_output = (255, 0, 128)
    assert fix_colour_string(input_str) == expected_output


def test_fix_colour_string_too_large_values() -> None:
    """
    Test conversion of invalid colour string to tuple.
    """
    input_str = "(-255, 0, 1028)"
    expected_output = (255, 0, 255)
    assert fix_colour_string(input_str) == expected_output
    assert fix_colour_string(input_str) == expected_output
    assert fix_colour_string(input_str) == expected_output
