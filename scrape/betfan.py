"""

    scrape.betfan.py
    ~~~~~~~~~~~~~~~~~
    Scrape https://betfan.pl for tennis odds.

    @author: z33k

"""
import json
from typing import List, Tuple
from time import sleep

import requests

from scrape import Json, Odds, OddsPair


class BetfanOdds(Odds):
    """betfan.pl's specific implementation of Odds interface.
    """
    def __init__(self, contender: str, odds: float) -> None:
        self._contender = contender
        self._odds = odds
        super().__init__()

    def _get_odds(self) -> float:
        return self._odds

    def _get_contender(self) -> str:
        return self._contender


def _get_cats() -> List[int]:
    url = "https://betfan.pl/rest/market/categories"
    r = requests.get(url).text
    data = json.loads(r)["data"]
    tennisdata = [item for item in data if "Tenis" in item["sportName"]]
    wta_data = [item for item in tennisdata
                if "WTA" in item["categoryName"] and len(item["categoryName"]) > 3]
    atp_data = [item for item in tennisdata
                if "ATP" in item["categoryName"] and len(item["categoryName"]) > 3]
    print(f"Retrieved {len(wta_data)} WTA and {len(atp_data)} ATP tournaments for further parsing.")
    return [item["categoryId"] for item in [*wta_data, *atp_data]]


def _get_events(*cat_ids: int) -> List[Json]:
    print(f"Retrieving events for {len(cat_ids)} tournaments(s).")
    url_template = "https://betfan.pl/rest/market/categories/multi/{}/events"
    events = []
    for id_ in cat_ids:
        r = requests.get(url_template.format(id_)).text
        data = json.loads(r)["data"]
        events.extend(data)
        print("Throttling for 700 ms..")
        sleep(0.7)
        print("Resumed.")
    print(f"Retrieved {len(events)} event(s) for further parsing.")
    return events


def _parse_event(event: Json) -> OddsPair:
    """Parse an 'eventId' object in betfan.pl's input for odds rendered as an OddsPair object.
    """
    event_games = event["eventGames"]
    eg = next((item for item in event_games if "Zwycięzca" == item["gameName"]), None)
    if eg is None:
        raise ValueError(f"Invalid input: {event}")
    odds = []
    for outcome in eg["outcomes"]:
        odds.append(BetfanOdds(outcome["outcomeName"], outcome["outcomeOdds"]))
    if len(odds) != 2:
        raise ValueError(f"Invalid input: {event}")
    home, away = odds
    return OddsPair(home, away)


def getpairs() -> List[OddsPair]:
    """Return a list of all betfan.pl's WTA and ATP odds pairs.
    """
    cats = _get_cats()
    events = _get_events(*cats)
    pairs = [_parse_event(e) for e in events]
    print(f"Got {len(pairs)} BETFAN odds pairs.")
    return pairs


