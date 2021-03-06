"""

    scrape.etoto.py
    ~~~~~~~~~~~~~~~~~
    Scrape https://www.etoto.pl for tennis odds.

    @author: z33k

    NOTE: this scrapes all WTA + ATP events, but there's no guarantee Grand Slams are included in
    this data.

"""
from typing import List

from scrape import Odds, OddsPair, CategorizedEventsParser

CATURL = "https://api.etoto.pl/rest/market/categories"
EVENT_URL_TEMPLATE = "https://api.etoto.pl/rest/market/categories/multi/{}/events"


class EtotoOdds(Odds):
    """www.etoto.pl's odds.
    """
    PROVIDER = "ETOTO"

    def __init__(self, contender: str, odds: float) -> None:
        super().__init__(contender, odds)


def getpairs() -> List[OddsPair]:
    """Return a list of all betfan.pl's WTA and ATP odds pairs.
    """
    parser = CategorizedEventsParser(CATURL, EVENT_URL_TEMPLATE, EtotoOdds)
    return parser.getpairs()


