"""

    scrape.fortuna.py
    ~~~~~~~~~~~~~~~~~
    Scrape https://www.efortuna.pl for tennis odds.

    @author: z33k

    NOTE: this scrapes all WTA + ATP events, but there's no guarantee Grand Slams are included in
    this data.

"""
from typing import List, Tuple

from bs4 import BeautifulSoup
from bs4.element import Tag
import pandas as pd

from scrape import Odds, OddsPair
from utils import timed_request

URL = "https://www.efortuna.pl/zaklady-bukmacherskie/tenis-mpl283"


def _get_tables() -> List[Tuple[Tag, str]]:
    def prune(text: str) -> bool:
        return any(w in text for w in ("WTA", "ATP")) and all(w not in text
                                                              for w in ("ITF", "Chall", "debel",
                                                                        "końc."))
    markup = timed_request(URL, provider=FortunaOdds.PROVIDER)
    soup = BeautifulSoup(markup, "lxml")
    sections = soup.select("section.competition-box")
    pruned = [s for s in sections if s.find("span", class_="competition-name", text=prune)]
    # e.g. "K-WTA Chicago 2, singiel"
    events = [p.find("span", class_="competition-name").text for p in pruned]
    new_events = []
    for e in events:
        _, second, *_ = e.split("-")
        # new_event, e.g.: "WTA Chicago 2, singiel"
        first, _ = second.split(",")
        # new_event, e.g.: "WTA Chicago 2"
        new_events.append(first.strip())
    print(f"Parsed {len(pruned)} table(s).")
    return [(p.find("table"), e) for p, e in zip(pruned, new_events)]


class FortunaOdds(Odds):
    """www.efortuna.pl's odds.
    """
    PROVIDER = "Fortuna"

    def __init__(self, contender: str, odds: float) -> None:
        super().__init__(contender, odds)


def _parse_table(table: Tag, event: str) -> List[OddsPair]:
    def filter_rows(od1: float, od2: float) -> bool:
        return bool(od1) and bool(od2)

    def parse_name(nm: str) -> str:
        first, second, *_ = nm.split(".")
        second = second.lstrip(" - ")
        first, second = f"{first}.", f"{second}."
        firstparts, secondparts = reversed(first.split()), reversed(second.split())
        return f"{' '.join(firstparts)}, {' '.join(secondparts)}"

    df = next(iter(pd.read_html(str(table))))
    df = df[df[["1", "2"]].apply(lambda x: filter_rows(*x), axis=1)]
    df = df.loc[~df.iloc[:, 0].str.contains("LIVE")]  # pruning LIVE events
    names = df.iloc[:, 0].apply(parse_name)
    odds1 = df["1"]
    odds2 = df["2"]
    pairs = []
    for name, o1, o2 in zip(names, odds1, odds2):
        name1, name2 = name.split(", ")
        pairs.append(OddsPair(FortunaOdds(name1, o1), FortunaOdds(name2, o2), event))
    print(f"Got {len(pairs)} odds pair(s) from table.")
    return pairs


def getpairs() -> List[OddsPair]:
    tables = _get_tables()
    pairs = [p for lst in [_parse_table(t, e) for t, e in tables] for p in lst]
    print(f"Got total number of {len(pairs)} {FortunaOdds.PROVIDER} odds pair(s).")
    return pairs

