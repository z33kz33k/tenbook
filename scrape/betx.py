"""

    scrape.betx.py
    ~~~~~~~~~~~~~~
    Scrape https://ebetx.pl for tennis odds.

    @author: z33k

    NOTE: this scrapes all WTA + ATP matches, but there's no guarantee Grand Slams are included in
    this data.

"""
from datetime import datetime
from typing import List

import requests

from scrape import Json, Odds, OddsPair


def _get_postdata() -> Json:
    now = datetime.now()
    year_after = datetime(now.year + 1, now.month, now.day, now.hour)
    return {
        "Offset": 0,
        "Limit": 50,
        "SportIds": [389],
        "CategoryIds": [],
        "LeagueIds": [],
        "DateFrom": now.isoformat(),
        "DateTo": year_after.isoformat()
    }


class BetxOdds(Odds):
    """ebetx.pl's specific implementation of Odds interface.
    """
    def __init__(self, contender: str, odds: float) -> None:
        self._contender = contender
        self._odds = odds
        super().__init__()

    def _get_odds(self) -> float:
        return self._odds

    def _get_contender(self) -> str:
        return self._contender


def _get_matches() -> List[Json]:
    url = "https://sportapis.ebetx.pl/SportOfferApi/api/sport/offer/v2/sports/offer"
    r = requests.post(url, json=_get_postdata())
    data = r.json()["Response"][0]
    tournaments = [t for item in data["Categories"] for t in item["Leagues"]]
    matches = [item for t in tournaments for item in t["Matches"]]
    print(f"Retrieved {len(matches)} match(es) for further parsing.")
    return matches


def _parse_match(match: Json) -> OddsPair:
    home_contender, away_contender = match["TeamHome"], match["TeamAway"]
    home_odds, away_odds = match["BasicOffer"]["Odds"]
    return OddsPair(BetxOdds(home_contender, home_odds["Odd"]),
                    BetxOdds(away_contender, away_odds["Odd"]))


def getpairs() -> List[OddsPair]:
    """Return a list of all ebetx.pl's WTA and ATP odds pairs.
    """
    pairs = [_parse_match(m) for m in _get_matches()]
    print(f"Got {len(pairs)} BetX odds pairs.")
    return pairs
