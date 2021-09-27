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


class EtotoOdds(Odds):
    """www.etoto.pl's odds.
    """
    PROVIDER = "ETOTO"

    def __init__(self, contender: str, odds: float) -> None:
        super().__init__(contender, odds)


def getpairs() -> List[OddsPair]:
    """Return a list of all betfan.pl's WTA and ATP odds pairs.
    """
    caturl = "https://api.etoto.pl/rest/market/categories"
    event_url_template = "https://api.etoto.pl/rest/market/categories/multi/{}/events"
    parser = CategorizedEventsParser(caturl, event_url_template, EtotoOdds)
    return parser.getpairs()


