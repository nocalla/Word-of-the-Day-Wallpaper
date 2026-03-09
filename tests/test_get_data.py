import logging

import pytest
import requests

from src.get_wotd import get_data


class _FakeResponse:
    def __init__(self, text: str) -> None:
        self.text = text

    def raise_for_status(self) -> None:
        return


def test_get_data_retries_with_backoff_before_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    attempts = {"count": 0}
    sleep_calls = []

    def fake_get(*args, **kwargs):
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise requests.ConnectionError("temporary network issue")
        return _FakeResponse("<html>ok</html>")

    monkeypatch.setattr("src.get_wotd.requests.get", fake_get)
    monkeypatch.setattr("src.get_wotd.time.sleep", lambda duration: sleep_calls.append(duration))

    data = get_data("https://example.com")

    assert data == "<html>ok</html>"
    assert attempts["count"] == 3
    assert sleep_calls == [1.0, 2.0]


def test_get_data_logs_and_raises_after_retry_exhaustion(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    sleep_calls = []

    def fake_get(*args, **kwargs):
        raise requests.Timeout("service unavailable")

    monkeypatch.setattr("src.get_wotd.requests.get", fake_get)
    monkeypatch.setattr("src.get_wotd.time.sleep", lambda duration: sleep_calls.append(duration))
    caplog.set_level(logging.ERROR)

    with pytest.raises(requests.Timeout):
        get_data("https://example.com")

    assert sleep_calls == [1.0, 2.0, 4.0]
    assert "failed to fetch word of the day after 4 attempts" in caplog.text
