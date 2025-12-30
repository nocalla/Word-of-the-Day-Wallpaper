import re
from html.entities import name2codepoint
from html.parser import HTMLParser


class _HTMLToText(HTMLParser):
    def __init__(self) -> None:
        HTMLParser.__init__(self)
        self._buf = []
        self.hide_output = False

    def handle_starttag(self, tag, attrs) -> None:
        if tag in ("p", "br") and not self.hide_output:
            self._buf.append("\n")
        elif tag in ("script", "style"):
            self.hide_output = True

    def handle_startendtag(self, tag, attrs) -> None:
        if tag == "br":
            self._buf.append("\n")

    def handle_endtag(self, tag) -> None:
        if tag == "p":
            self._buf.append("\n")
        elif tag in ("script", "style"):
            self.hide_output = False

    def handle_data(self, text) -> None:
        if text and not self.hide_output:
            self._buf.append(re.sub(r"\s+", " ", text))

    def handle_entityref(self, name) -> None:
        if name in name2codepoint and not self.hide_output:
            c = chr(name2codepoint[name])
            self._buf.append(c)

    def handle_charref(self, name) -> None:
        if not self.hide_output:
            n = int(name[1:], 16) if name.startswith("x") else int(name)
            self._buf.append(chr(n))

    def get_text(self) -> str:
        return re.sub(r" +", " ", "".join(self._buf))
