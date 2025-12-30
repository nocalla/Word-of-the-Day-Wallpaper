import re
from dataclasses import dataclass

import requests

from .html_converter import _HTMLToText


@dataclass
class WordOfTheDay:
    word: str
    pronunciation: str
    category: str
    definition: str
    explanation: str
    example: str


def html_to_text(html) -> str:
    # from https://gist.github.com/Crazometer/af441bc7dc7353d41390a59f20f07b51
    """
    Given a piece of HTML, return the plain text it contains.
    This handles entities and char refs, but not javascript and stylesheets.
    """
    parser = _HTMLToText()
    parser.feed(html)
    parser.close()
    text = parser.get_text()
    text = text.replace("\n\n", " ")
    text = text.replace("  ", " ")

    return text


def get_data(source: str) -> str:
    """
    retrieves html data from source link
    :return: html text
    """
    data = requests.get(source)
    data.raise_for_status()
    return html_to_text(data.text)


def parse_wotd_data(text: str, regex_filter: str) -> WordOfTheDay:
    """
    parses the text from html_to_text to return a dictionary of word data
    :param text: text to parse
    :return: WordOfTheDay dataclass object with word data or None if no data found
    """

    re.compile(regex_filter, re.DOTALL)

    match = re.search(regex_filter, text)
    if not match:
        raise Exception("Error: no word data matching regex found.")

    return WordOfTheDay(
        word=match.group(1).capitalize().strip(),
        pronunciation=match.group(2).strip(),
        category=match.group(3).strip(),
        definition=match.group(4).strip(),
        explanation=match.group(5).strip(),
        example=match.group(6).strip(),
    )
