"""

    scrape
    ~~~~~~
    Scrape polish tennis bookies.

    @author: z33k

"""
import json
from abc import ABCMeta
from dataclasses import dataclass
from time import sleep
from typing import Any, Dict, Generator, List, Optional, Tuple, Type, Union

import requests

Json = Dict[str, Any]
THROTTLING_PERIOD = 0.5  # seconds


def percent(fraction: float, precision: int = 2) -> str:
    """Return fraction rendered as a percent string.
    """
    return f"{fraction * 100:.{precision}f}%"


class Odds(metaclass=ABCMeta):
    """Basic interface for Odds objects.
    """
    PROVIDER: Optional[str] = None

    def __init__(self, contender: str, odds: float) -> None:
        if type(self) is Odds:
            raise TypeError(f"Abstract class {self.__class__.__name__} must not be instantiated.")
        self.contender = self._normalize(contender)
        self.odds = odds

    @staticmethod
    def _normalize(contender) -> str:
        if "," in contender:
            lastname, firstname = contender.split(",")
            return f"{firstname.strip()} {lastname.strip()}"
        return contender

    def __str__(self) -> str:
        return f"({self.contender}, {self.odds:.2f})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(contender='{self.contender}', odds={self.odds:.2f})"

    def __eq__(self, other: "Odds") -> Union[bool, "NotImplemented"]:
        """Overload '==' operator.

        NOTE: this solution was based on:
        https://stackoverflow.com/questions/390250/elegant-ways-to-support-equivalence-equality-in-python-classes)
        """
        if isinstance(self, other.__class__):
            return self.contender == other.contender and self.odds == self.odds
        return NotImplemented

    def __hash__(self) -> int:
        """Make this object hashable
        """
        return hash(tuple(sorted(self.__dict__.items())))

    @property
    def as_percent(self) -> float:
        return 1 / self.odds


@dataclass
class OddsPair:
    """Pair of odds for one match.
    """
    home: Odds
    away: Odds
    event: str = ""

    def __repr__(self) -> str:
        repr_ = f"{self.__class__.__name__}([{self.home}, {self.away}], "
        repr_ += f"event='{self.event}', " if self.event else ""
        repr_ += f"provider='{self.home.PROVIDER}', spread={self.spread:.2f}, " \
                 f"margin={self.marginstr})"
        return repr_

    @property
    def as_tuple(self) -> Tuple[Odds, Odds]:
        return self.home, self.away

    @property
    def margin(self) -> float:
        return self.home.as_percent + self.away.as_percent - 1

    @property
    def marginstr(self) -> str:
        return percent(self.margin)

    @property
    def spread(self) -> float:
        return abs(self.home.odds - self.away.odds)

    @property
    def contenders(self) -> Tuple[str, str]:
        return self.home.contender, self.away.contender

    @property
    def nameparts(self) -> Generator[str, None, None]:
        """Return parts of contenders' names.

        E.g. for ("Paula Badosa Gibert", "Iga Świątek") it would be:
        ["Paula", "Badosa", "Gibert", "Iga", "Świątek"]
        """
        return (part for contender in self.contenders for part in contender.split())


def filter_pair(odds_list: List[Odds], home: str, away: str) -> Optional[OddsPair]:
    """Filter pair of odds from 'odds_list' based on 'home' and 'away'.

    NOTE: this relies on input 'home' and 'away' making sense to return a sensible output pair.
    """
    home_odds = next((o for o in odds_list if o.contender == home), None)
    if not home_odds:
        return None
    away_odds = next((o for o in odds_list if o.contender == away), None)
    if not away_odds:
        return None
    return OddsPair(home_odds, away_odds)


def pairs_to_odds(odds_pairs: List[OddsPair]) -> List[Odds]:
    """Return a flat list of all odds from odds_pairs.
    """
    odds = [o for pair in odds_pairs for o in pair.as_tuple]
    print(f"Converted {len(odds_pairs)} odds pair(s) to odds.")
    return odds


class CategorizedEventsParser:
    """Parser of sites with categorized events.

    Sites with categorized events need first to retrieve categories, and then based on this,
    a proper event URL can be parsed.

    The sites using this infrastructure:
    * betfan.pl
    * etoto.pl
    """
    def __init__(self, caturl: str, event_url_template: str, odds_type: Type[Odds],
                 throttling_period: float = THROTTLING_PERIOD) -> None:
        self.caturl = caturl
        self.event_url_template = event_url_template
        self.odds_type = odds_type
        self.throttling_period = throttling_period

    def _get_cats(self) -> List[int]:
        r = requests.get(self.caturl).text
        data = json.loads(r)["data"]
        # filtering
        tennisdata = [item for item in data if "Tenis" in item["sportName"]]
        to_exlude = ("sezonowe", "turniej", "ITF", "Challenger")
        wta_data = [item for item in tennisdata
                    if "WTA" in item["categoryName"] and len(item["categoryName"]) > 3
                    and not any(n in item["categoryName"] for n in to_exlude)]
        atp_data = [item for item in tennisdata
                    if "ATP" in item["categoryName"] and len(item["categoryName"]) > 3
                    and not any(n in item["categoryName"] for n in to_exlude)]
        print(f"Retrieved {len(wta_data)} WTA and {len(atp_data)} ATP tournaments for further "
              f"parsing.")
        return [item["categoryId"] for item in [*wta_data, *atp_data]]

    def _get_events(self, *cat_ids: int) -> List[Json]:
        print(f"Retrieving events for {len(cat_ids)} tournaments(s).")
        events = []
        for id_ in cat_ids:
            r = requests.get(self.event_url_template.format(id_)).text
            data = json.loads(r)["data"]
            events.extend(data)
            print(f"Throttling for {int(self.throttling_period * 1000)} ms..")
            sleep(self.throttling_period)
            print("Resumed.")
        print(f"Retrieved {len(events)} event(s) for further parsing.")
        return events

    def _parse_event(self, event: Json) -> Optional[OddsPair]:
        """Parse an 'eventId' object in betfan.pl's input for odds rendered as an OddsPair object.
        """
        event_games = event["eventGames"]
        eventname = event["category3Name"]
        eg = next((item for item in event_games if "Zwycięzca" == item["gameName"]), None)
        if eg is None:
            return None
        odds = []
        for outcome in eg["outcomes"]:
            if "/" in outcome["outcomeName"]:
                return None  # prune doubles
            odds.append(self.odds_type(outcome["outcomeName"], outcome["outcomeOdds"]))
        if len(odds) != 2:
            return None
        home, away = odds
        return OddsPair(home, away, eventname)

    def getpairs(self) -> List[OddsPair]:
        """Return a list of all betfan.pl's WTA and ATP odds pairs.
        """
        cats = self._get_cats()
        events = self._get_events(*cats)
        pairs = [self._parse_event(e) for e in events]
        pairs = [p for p in pairs if p]  # prune None
        print(f"Got {len(pairs)} {self.odds_type.PROVIDER} odds pairs.")
        return pairs
