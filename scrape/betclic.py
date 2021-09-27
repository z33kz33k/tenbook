"""

    scrape.betclic.py
    ~~~~~~~~~~~~~~~~~
    Scrape https://www.betclic.pl for tennis odds.

    @author: z33k

    NOTE: this scrapes all WTA + ATP events, but there's no guarantee Grand Slams are included in
    this data.

"""
from typing import List

import requests

from scrape import Json, Odds, OddsPair


class BetclicOdds(Odds):
    """betclic.pl's specific implementation of Odds interface.
    """
    def __init__(self, contender: str, odds: float) -> None:
        self._contender = contender
        self._odds = odds
        super().__init__()

    def _get_odds(self) -> float:
        return self._odds

    def _get_contender(self) -> str:
        return self._contender


def _get_events() -> List[Json]:
    url = "https://offer.cdn.begmedia.com/api/pub/v4/events?application=2048&countrycode=pl" \
      "&fetchMultipleDefaultMarkets=true&language=pa&limit=400&offset=0&sitecode=plpa&sortBy" \
      "=ByLiveRankingPreliveDate&sportIds=2"
    data = requests.get(url).json()
    # filter out 'live' events
    data = [e for e in data if not e['isLive']]
    to_exclude = ("Challenger", "ITF", "Exhibition")
    data = [e for e in data if not any(n in e["competition"]["name"] for n in to_exclude)]
    return [e for e in data if e["markets"]]


def _parse_event(event: Json) -> OddsPair:
    """Parse an event object in betclic.pl's input for odds rendered as an OddsPair object.
    """
    market = next((m for m in event["markets"] if m["name"] == "Zwycięzca meczu"), None)
    if not market:
        raise ValueError(f"Invalid input: {event}.")
    home, away = market["selections"]
    return OddsPair(BetclicOdds(home["name"], home["odds"]),
                    BetclicOdds(away["name"], away["odds"]))


def getpairs() -> List[OddsPair]:
    """Return a list of all betclic.pl's WTA and ATP odds pairs.
    """
    pairs = [_parse_event(e) for e in _get_events()]
    print(f"Got {len(pairs)} Betclic odds pairs.")
    return pairs

