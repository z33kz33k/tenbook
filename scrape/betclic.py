"""

    scrape.betclic.py
    ~~~~~~~~~~~~~~~~~
    Scrape https://www.betclic.pl for tennis odds.

    @author: z33k

"""
from typing import List

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from scrape import OddsUnavailableError


URL = "https://www.betclic.pl/tenis-s2"


class Odds:
    """betclic.pl's odds.
    """
    def __init__(self, bs_tag: Tag) -> None:
        self._bs_tag = bs_tag
        self.odds: float = self._get_odds()
        self.contender: str = self._get_contender()

    def _get_contender(self) -> str:
        tag = self._bs_tag.find(lambda tg: tg.name == "div" and "oddButtonWrapper" in tg.get(
            "class"))
        return tag.get("title")

    def _get_odds(self) -> float:
        tag = self._bs_tag.find(lambda tg: tg.name == "span" and "oddValue" in tg.get("class"))
        if "-" in tag.text or "Postaw" in tag.text:
            raise OddsUnavailableError("Odds unavailable at present.")
        return float(tag.text.replace(",", "."))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(contender='{self.contender}', odds={self.odds})"


def getodds() -> List[Odds]:
    """Return a list of all betclic.pl's tennis odds.
    """
    markup = requests.get(URL).text
    soup = BeautifulSoup(markup, "lxml")
    events_tag = soup.find(lambda t: t.name == "sports-events-list")
    button_tags = events_tag.find_all("sports-selections-selection")
    odds = []
    for tag in button_tags:
        try:
            o = Odds(tag)
        except OddsUnavailableError:
            continue
        odds.append(o)
    return odds


