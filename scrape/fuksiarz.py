"""

    scrape.fuksiarz.py
    ~~~~~~~~~~~~~~~~~
    Scrape https://fuksiarz.pl for tennis odds.

    @author: z33k

    NOTE: this scrapes all WTA + ATP events, but there's no guarantee Grand Slams are included in
    this data.

"""
from typing import List

from scrape import CategorizedEventsParser, Odds, OddsPair

CATURL = "https://fuksiarz.pl/rest/market/categories"
EVENT_URL_TEMPLATE = "https://fuksiarz.pl/rest/market/categories/multi/{}/events"


class FuksiarzOdds(Odds):
    """fuksiarz.pl's odds.
    """
    PROVIDER = "Fuksiarz"

    def __init__(self, contender: str, odds: float) -> None:
        super().__init__(contender, odds)


def getpairs() -> List[OddsPair]:
    """Return a list of all betfan.pl's WTA and ATP odds pairs.
    """
    parser = CategorizedEventsParser(CATURL, EVENT_URL_TEMPLATE, FuksiarzOdds)
    return parser.getpairs()

