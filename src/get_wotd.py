import json
import logging
import re
import time
from dataclasses import dataclass
from html import unescape

import requests

from html_converter import html_to_text

LOGGER = logging.getLogger(__name__)
REQUEST_TIMEOUT_SECONDS = 15
MAX_FETCH_RETRIES = 3
BACKOFF_BASE_SECONDS = 1.0


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
    :param source: url to retrieve
    :return: raw html text
    """
    for attempt in range(MAX_FETCH_RETRIES + 1):
        try:
            data = requests.get(source, timeout=REQUEST_TIMEOUT_SECONDS)
            data.raise_for_status()
            return data.text
        except requests.RequestException as exc:
            if attempt == MAX_FETCH_RETRIES:
                LOGGER.error(
                    "failed to fetch word of the day after %d attempts from %s: %s",
                    MAX_FETCH_RETRIES + 1,
                    source,
                    exc,
                )
                raise

            sleep_seconds = BACKOFF_BASE_SECONDS * (2**attempt)
            LOGGER.warning(
                "request attempt %d/%d for %s failed: %s; retrying in %.1f seconds",
                attempt + 1,
                MAX_FETCH_RETRIES + 1,
                source,
                exc,
                sleep_seconds,
            )
            time.sleep(sleep_seconds)

    raise RuntimeError("unreachable retry state reached while fetching word data")


def _clean_text(value: str) -> str:
    """
    strip html tags, decode entities, and normalize whitespace
    :param value: source text that may contain html and entity encodings
    :return: cleaned text
    """
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", "", value))).strip()


def _parse_from_embedded_json(page_html: str) -> WordOfTheDay | None:
    """
    parse the current word of the day from dictionary.com's embedded json payload
    :param page_html: raw response html
    :return: WordOfTheDay if parsing succeeds, else None
    """
    # Dictionary.com exposes a stable JSON payload for the latest word in this script tag.
    match = re.search(
        r"<script[^>]*\bid=['\"]json-current-wotd['\"][^>]*>\s*(\{.*?\})\s*</script>",
        page_html,
        flags=re.DOTALL,
    )
    if not match:
        return None

    try:
        payload = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        LOGGER.warning("embedded word-of-the-day json was not valid: %s", exc)
        return None

    field_paths = {
        "word": ("headword",),
        "pronunciation": ("pronunciation", "phonetic", "html"),
        "category": ("partOfSpeech",),
        "definition": ("definition",),
        "explanation": ("body",),
        "example": ("exampleSentence",),
    }
    extracted_fields = {
        field_name: _clean_text(_get_payload_field(payload, path))
        for field_name, path in field_paths.items()
    }

    missing_fields = [
        field_name for field_name, value in extracted_fields.items() if not value
    ]
    if missing_fields:
        payload_keys = ", ".join(sorted(payload.keys()))
        missing_labels = ", ".join(missing_fields)
        LOGGER.error(
            "embedded word-of-the-day json is missing required fields: %s; available top-level keys: %s",
            missing_labels,
            payload_keys,
        )
        raise ValueError(
            f"Embedded word-of-the-day JSON is missing required fields: {missing_labels}"
        )

    return WordOfTheDay(
        word=extracted_fields["word"].capitalize(),
        pronunciation=extracted_fields["pronunciation"],
        category=extracted_fields["category"],
        definition=extracted_fields["definition"],
        explanation=extracted_fields["explanation"],
        example=extracted_fields["example"],
    )


def _get_payload_field(payload: dict, path: tuple[str, ...]) -> str:
    """
    safely retrieve a nested field from a json payload
    :param payload: json object decoded from embedded response
    :param path: ordered path to the nested field
    :return: field value if found, else empty string
    """
    current_value = payload
    for key in path:
        if not isinstance(current_value, dict):
            return ""
        current_value = current_value.get(key)

    if isinstance(current_value, str):
        return current_value
    return ""


def parse_wotd_data(page_html: str, regex_filter: str | None = None) -> WordOfTheDay:
    """
    parses html from dictionary.com to return structured word data
    :param page_html: html to parse
    :param regex_filter: optional regex for fallback text parsing
    :return: WordOfTheDay dataclass object with word data
    """
    json_wotd = _parse_from_embedded_json(page_html)
    if json_wotd:
        return json_wotd

    text = html_to_text(page_html)
    fallback_regex = (
        regex_filter
        or r"[A-Za-z]+\s+\d{1,2},\s+\d{4}\s+([^\[\n]+?)\s+\[([^\]]+)\]\s+([A-Za-z ]+?)\s+(.+?)\s+Explanation\s+(.+?)\s+Example\s+(.+?)(?:\s+[A-Za-z]+\s+\d{1,2},\s+\d{4}|\s+1\s+2\s+3|$)"
    )

    match = re.search(fallback_regex, text, flags=re.DOTALL)
    if not match:
        LOGGER.error(
            "could not parse word-of-the-day data from response text fallback; source text sample: %s",
            text[:250],
        )
        raise ValueError("Error: could not parse word data from response.")

    return WordOfTheDay(
        word=_clean_text(match.group(1)).capitalize(),
        pronunciation=_clean_text(match.group(2)),
        category=_clean_text(match.group(3)),
        definition=_clean_text(match.group(4)),
        explanation=_clean_text(match.group(5)),
        example=_clean_text(match.group(6)),
    )
