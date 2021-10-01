"""

    scrape.betx.py
    ~~~~~~~~~~~~~~
    Scrape https://ebetx.pl for tennis odds.

    @author: z33k

    NOTE: this scrapes all WTA + ATP matches, but there's no guarantee Grand Slams are included in
    this data.

"""
from datetime import datetime
from typing import List, Optional

import requests

from scrape import Json, Odds, OddsPair

URL = "https://sportapis.ebetx.pl/SportOfferApi/api/sport/offer/v2/sports/offer"


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
    """ebetx.pl's odds.
    """
    PROVIDER = "BetX"

    def __init__(self, contender: str, odds: float) -> None:
        super().__init__(contender, odds)


def _get_matches() -> List[Json]:
    r = requests.post(URL, json=_get_postdata())
    data = r.json()["Response"][0]
    tournaments = [t for item in data["Categories"] for t in item["Leagues"]]
    tournaments = [t for t in tournaments if all(w not in t["Name"] for w in ("ITF", "Challenger"))]
    matches = [item for t in tournaments for item in t["Matches"]]
    print(f"Retrieved {len(matches)} match(es) for further parsing.")
    return matches


def _parse_match(match: Json) -> Optional[OddsPair]:
    home_contender, away_contender = match["TeamHome"], match["TeamAway"]
    if any("/" in n for n in (home_contender, away_contender)):
        return None  # prune doubles
    home_odds, away_odds = match["BasicOffer"]["Odds"]
    return OddsPair(BetxOdds(home_contender, home_odds["Odd"]),
                    BetxOdds(away_contender, away_odds["Odd"]))


def getpairs() -> List[OddsPair]:
    """Return a list of all ebetx.pl's WTA and ATP odds pairs.
    """
    pairs = [_parse_match(m) for m in _get_matches()]
    pairs = [p for p in pairs if p]  # prune doubles
    print(f"Got {len(pairs)} {BetxOdds.PROVIDER} odds pairs.")
    return pairs
