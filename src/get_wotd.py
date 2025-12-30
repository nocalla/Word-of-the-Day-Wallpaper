import re
from dataclasses import dataclass

import requests

from html_converter import html_to_text


@dataclass
class WordOfTheDay:
    word: str
    pronunciation: str
    category: str
    definition: str
    explanation: str
    example: str


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
