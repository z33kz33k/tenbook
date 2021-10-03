"""

    scrape.lv_bet.py
    ~~~~~~~~~~~~~~~~~
    Scrape https://lvbet.pl for tennis odds.

    @author: z33k

    NOTE: this scrapes all WTA + ATP events, but there's no guarantee Grand Slams are included in
    this data.

"""
from typing import Dict, List, Optional

import requests
from contexttimer import Timer

from scrape import Json, Odds, OddsPair

URL = "https://app.lvbet.pl/_api/v1/offer/matches/?is_live=false&lang=pl"


def _get_matches() -> List[Json]:
    print(f"Retrieving data from LV BET servers...")
    with Timer() as t:
        data = requests.get(URL).json()
    print(f"Request completed in {t.elapsed:.3f} seconds.")

    matches = [d for d in data if d["group"]["label"] == "tennis"]
    print(f"Parsed {len(matches)} match(es).")
    return matches


class LvBetOdds(Odds):
    """lvbet.pl's odds.
    """
    PROVIDER = "LV BET"

    def __init__(self, contender: str, odds: float) -> None:
        super().__init__(contender, odds)


def _parse_match(match: Json) -> Optional[OddsPair]:
    # parse json for event, return None for invalid input
    sports_groups = match["sportsGroups"]
    if len(sports_groups) != 3:
        return None
    event = sports_groups[2]["name"]
    to_exlude = ("ITF", "Challenger", "UTR", "deble", "Pro Series", "Doubles")
    if any(w in event for w in to_exlude):
        return None
    event, _ = event.split(" - ")

    if len(match["participants"]) != 2:
        return None
    contenders: Dict[str, str] = match["participants"]
    if any("/" in name for name in contenders.values()):
        return None  # prune doubles (if they still persist)

    market = next((mkt for mkt in match["primaryMarkets"] if "match-winner" in mkt.values()), None)
    if not market:
        return None

    selections = market["selections"]
    if len(selections) != 2:
        return None

    odds = []
    for s in selections:
        name = s["name"]
        if name not in contenders.values():
            return None
        rate = s["rate"]["decimal"]
        odds.append(LvBetOdds(name, rate))

    return OddsPair(*odds, event)


def getpairs() -> List[OddsPair]:
    matches = _get_matches()
    pairs = [_parse_match(match) for match in matches]
    pairs = [p for p in pairs if p]
    print(f"Got total number of {len(pairs)} {LvBetOdds.PROVIDER} odds pair(s).")
    return pairs




