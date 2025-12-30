import pytest

from src.get_wotd import WordOfTheDay, html_to_text, parse_wotd_data

WOTD_FILTER = r"\d{2}\, \d{4} (.*)\s\[(.*)\]\s(.*)\s(.*)\s.*\s(.*)\s.*\s(.*)"


@pytest.fixture
def request_html_as_text() -> str:
    with open(
        r"C:\Users\Niall\Development\Programs\python\projects\wotd_wallpaper\test\test_response.html",
        "r",
        encoding="utf-8",
    ) as f:
        html_content = f.read()
        text = html_to_text(html_content)
    return text


def test_parse_wotd_data(request_html_as_text: str) -> None:
    """
    Test parsing of word of the day data.
    """

    expected_output = WordOfTheDay(
        word="Mascot",
        category="noun",
        definition="an animal, person, or thing adopted by a group as its representative symbol and supposed to bring good luck",
        pronunciation="mas-kot",
        explanation="A mascot is more than a costumed character — it's a symbol meant to embody the spirit, luck, or identity of a group. Whether it's a lion prowling the sidelines or a lucky trinket hanging from a rearview mirror, a mascot gives form to shared pride and purpose.",
        example="The team's mascot, a tiger, rallied the fans with its energetic antics.",
    )

    test_output = parse_wotd_data(
        request_html_as_text,
        WOTD_FILTER,
    )
    assert test_output == expected_output
