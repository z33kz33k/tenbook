"""

    scrape.betclic.py
    ~~~~~~~~~~~~~~~~~
    Scrape https://www.betclic.pl for tennis odds.

    @author: z33k

    NOTE: this scrapes all WTA + ATP events, but there's no guarantee Grand Slams are included in
    this data.

"""
from typing import List, Optional

import requests

from scrape import Json, Odds, OddsPair

URL = "https://offer.cdn.begmedia.com/api/pub/v4/events?application=2048&countrycode=pl" \
  "&fetchMultipleDefaultMarkets=true&language=pa&limit=400&offset=0&sitecode=plpa&sortBy" \
  "=ByLiveRankingPreliveDate&sportIds=2"


class BetclicOdds(Odds):
    """betclic.pl's odds.
    """
    PROVIDER = "Betclic"

    def __init__(self, contender: str, odds: float) -> None:
        super().__init__(contender, odds)


def _get_events() -> List[Json]:
    data = requests.get(URL).json()
    # filter out 'live' events
    data = [e for e in data if not e['isLive']]
    to_exclude = ("Challenger", "ITF", "Exhibition")
    data = [e for e in data if not any(n in e["competition"]["name"] for n in to_exclude)]
    data = [e for e in data if any(n in e["competition"]["name"] for n in ("WTA", "ATP"))]
    return [e for e in data if e["markets"]]


def _parse_event(event: Json) -> Optional[OddsPair]:
    """Parse an event object in betclic.pl's input for odds rendered as an OddsPair object.
    """
    eventname = event["competition"]["name"]
    market = next((m for m in event["markets"] if m["name"] == "Zwycięzca meczu"), None)
    if not market:
        return None
    home, away = market["selections"]

    if any("/" in n for n in (home["name"], away["name"])):
        return None  # prune doubles

    return OddsPair(BetclicOdds(home["name"], home["odds"]),
                    BetclicOdds(away["name"], away["odds"]),
                    eventname)


def getpairs() -> List[OddsPair]:
    """Return a list of all betclic.pl's WTA and ATP odds pairs.
    """
    pairs = [_parse_event(e) for e in _get_events()]
    pairs = [p for p in pairs if p]  # prune None
    print(f"Got {len(pairs)} {BetclicOdds.PROVIDER} odds pairs.")
    return pairs

