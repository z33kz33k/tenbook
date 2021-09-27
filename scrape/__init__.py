"""

    scrape
    ~~~~~~
    Scrape polish tennis bookies.

    @author: z33k

"""
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from bs4.element import Tag

Json = Dict[str, Any]


class OddsUnavailableError(ValueError):
    """Raised when even though scraping works, odds are still unavailable.
    """


class Odds(metaclass=ABCMeta):
    """Basic interface for Odds objects.
    """
    def __init__(self) -> None:
        if type(self) is Odds:
            raise TypeError(f"Abstract class {self.__class__.__name__} must not be instantiated.")
        self.odds: float = self._get_odds()
        self.contender: str = self._get_contender()

    @abstractmethod
    def _get_contender(self) -> str:
        ...

    @abstractmethod
    def _get_odds(self) -> float:
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(contender='{self.contender}', odds={self.odds})"


class BsOdds(Odds):
    """Odds scraped from a static page with BeautifulSoup.
    """
    def __init__(self, bs_tag: Tag) -> None:
        if type(self) is BsOdds:
            raise TypeError(f"Abstract class {self.__class__.__name__} must not be instantiated.")
        self._bs_tag = bs_tag
        super().__init__()

    @abstractmethod
    def _get_contender(self) -> str:
        ...

    @abstractmethod
    def _get_odds(self) -> float:
        ...


@dataclass
class OddsPair:
    """Pair of odds for one match.
    """
    home: Odds
    away: Odds

    @property
    def margin(self) -> float:
        return 1 / self.home.odds + 1 / self.away.odds - 1

    @property
    def marginstr(self) -> str:
        return f"{self.margin * 100:.2f} %"

    @property
    def as_tuple(self) -> Tuple[Odds, Odds]:
        return self.home, self.away


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

