"""

    scrape.betfan.py
    ~~~~~~~~~~~~~~~~~
    Scrape https://betfan.pl for tennis odds.

    @author: z33k

    NOTE: this scrapes all WTA + ATP events, but there's no guarantee Grand Slams are included in
    this data.

"""
from typing import List

from scrape import Odds, OddsPair, CategorizedEventsParser

CATURL = "https://betfan.pl/rest/market/categories"
EVENT_URL_TEMPLATE = "https://betfan.pl/rest/market/categories/multi/{}/events"


class BetfanOdds(Odds):
    """betfan.pl's odds.
    """
    PROVIDER = "BETFAN"

    def __init__(self, contender: str, odds: float) -> None:
        super().__init__(contender, odds)


def getpairs() -> List[OddsPair]:
    """Return a list of all betfan.pl's WTA and ATP odds pairs.
    """
    parser = CategorizedEventsParser(CATURL, EVENT_URL_TEMPLATE, BetfanOdds)
    return parser.getpairs()
