import logging

import pytest

from src.get_wotd import WordOfTheDay, parse_wotd_data


@pytest.fixture
def request_html_as_text() -> str:
    with open(
        r"tests/test_response_text.txt",
        "r",
        encoding="utf-8",
    ) as f:
        text = f.read()
    return text


@pytest.fixture
def request_html() -> str:
    with open(
        r"tests/test_response.html",
        "r",
        encoding="utf-8",
    ) as f:
        text = f.read()
    return text


@pytest.fixture
def request_new_layout_html() -> str:
    with open(
        r"tests/test_response_new_layout.html",
        "r",
        encoding="utf-8",
    ) as f:
        text = f.read()
    return text


def test_parse_wotd_data_from_html_json(request_html: str) -> None:
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

    test_output = parse_wotd_data(request_html)
    assert test_output == expected_output


def test_parse_wotd_data_from_text_fallback(request_html_as_text: str) -> None:
    expected_output = WordOfTheDay(
        word="Mascot",
        category="noun",
        definition="an animal, person, or thing adopted by a group as its representative symbol and supposed to bring good luck",
        pronunciation="mas-kot",
        explanation="A mascot is more than a costumed character — it's a symbol meant to embody the spirit, luck, or identity of a group. Whether it's a lion prowling the sidelines or a lucky trinket hanging from a rearview mirror, a mascot gives form to shared pride and purpose.",
        example="The team's mascot, a tiger, rallied the fans with its energetic antics.",
    )

    test_output = parse_wotd_data(request_html_as_text)
    assert test_output == expected_output


def test_parse_wotd_data_from_new_layout_fixture(request_new_layout_html: str) -> None:
    expected_output = WordOfTheDay(
        word="Sonder",
        category="noun",
        definition="the realization that each random passerby is living a life as vivid and complex as your own",
        pronunciation="son-der",
        explanation="Sonder captures a powerful shift in perspective - seeing strangers as full people with their own stories.",
        example="On the train, she felt a sudden sense of sonder while watching everyone head home.",
    )

    test_output = parse_wotd_data(request_new_layout_html)
    assert test_output == expected_output


def test_parse_wotd_data_logs_and_fails_on_missing_required_json_fields(
    caplog: pytest.LogCaptureFixture,
) -> None:
    invalid_payload_html = """
        <html>
            <body>
                <script id="json-current-wotd" type="application/json">
                    {
                        "headword": "sonder",
                        "partOfSpeech": "noun",
                        "body": "A perspective shift.",
                        "pronunciation": {"phonetic": {"html": "son-der"}}
                    }
                </script>
            </body>
        </html>
    """
    caplog.set_level(logging.ERROR)

    with pytest.raises(ValueError, match="missing required fields"):
        parse_wotd_data(invalid_payload_html)

    assert "missing required fields: definition, example" in caplog.text
