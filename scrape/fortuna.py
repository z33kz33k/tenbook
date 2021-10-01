"""

    scrape.fortuna.py
    ~~~~~~~~~~~~~~~~~
    Scrape https://www.efortuna.pl for tennis odds.

    @author: z33k

    NOTE: this scrapes all WTA + ATP events, but there's no guarantee Grand Slams are included in
    this data.

"""
from typing import List

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
import pandas as pd

URL = "https://www.efortuna.pl/zaklady-bukmacherskie/tenis-mpl283"


def _prune(text: str) -> bool:
    return any(w in text for w in ("WTA", "ATP") and all(w not in text for w in ("ITF", "Chall",
                                                                                 "debel")))


def _get_tables() -> List[Tag]:
    markup = requests.get(URL).text
    soup = BeautifulSoup(markup, "lxml")
    sections = soup.select("section.competition-box")
    pruned = [s for s in sections if s.find("span", class_="competition-name", text=_prune)]
    return [p.find("table") for p in pruned]


