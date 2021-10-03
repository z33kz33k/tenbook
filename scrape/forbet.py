"""

    scrape.forbet.py
    ~~~~~~~~~~~~~~~~~
    Scrape https://www.iforbet.pl for tennis odds.

    @author: z33k

    NOTE: this scrapes all WTA + ATP events, but there's no guarantee Grand Slams are included in
    this data.

"""
from time import sleep
from typing import Generator, List

from bs4 import BeautifulSoup
from bs4.element import Tag

from scrape import Odds, OddsPair

from utils import timed_request

# the usual approach of looking at what gets requested by the page failed here
# not only because the data needed is not within jsons returned (oddly, it lurks in one of returned
# html's), but because even though this url/html is hit after clicking on "Tenis" category,
# it only includes ATP data - WTA is missing (and it's not displayed on the page too)
#
# that is why parsing WTA data requires somewhat more involved approach:
# first one has to determine what are category ids and then request category-specific data

MAINURL = "https://www.iforbet.pl/zaklady-bukmacherskie"
THROTTLING_PERIOD = 0.7


# ceased to work
# def _get_cat_ids() -> List[int]:
#     # markup = requests.get(MAINURL).text
#     markup = timed_request(MAINURL, provider=ForbetOdds.PROVIDER)
#     soup = BeautifulSoup(markup, "lxml")
#     div = soup.find("div", class_="image banner-image", title="Tenis")
#     # e.g: 'redirectPage(\'oferta/8/55606,55617,41413,41418,55607,55604,55626,55615\',\'_self\')'
#     text = div.attrs["onclick"]
#     _, second = text.split("oferta/8/")
#     first, _ = second.split(r"',")
#     catids = [int(p) for p in first.split(",")]
#     print(f"Parsed {len(catids)} category(ies).")
#     return catids


def _get_cat_ids() -> List[int]:
    markup = timed_request(MAINURL, provider=ForbetOdds.PROVIDER)
    soup = BeautifulSoup(markup, "lxml")
    cat5div = soup.select("div#cat-5")[0]

    cat2divs = cat5div.find_all("div", class_="cat2 hide")
    new_cat2divs = []
    for c in cat2divs:
        tdiv = c.find("div", class_="title")
        span = tdiv.find("span")
        if any(w in span.text for w in ("ATP", "WTA")):
            new_cat2divs.append(c)

    catids = []
    for c in new_cat2divs:
        cat3divs = c.find_all("div", class_="cat3 hide")
        for div in cat3divs:
            id_ = div.attrs["id"]
            result = id_.split("-")[-1]
            catids.append(int(result))

    return catids


def urlgen() -> Generator[str, None, None]:
    template = "https://www.iforbet.pl/oferta/8/{}"
    for catid in _get_cat_ids():
        yield template.format(catid)


def _get_event_divs() -> List[Tag]:
    def validate_soup(bs: BeautifulSoup) -> bool:
        # search in soup for element displaying e.g: TENIS >> WTA >> WTA CHICAGO
        divs = bs.find_all("div", class_="left outcomes-menu uppercase tl")
        if len(divs) < 2:
            return False
        ass = divs[1].find_all("a")
        children = [*ass]
        if len(children) < 3:
            return False
        tag = children[2]
        # if it does not contain illegal words, it's OK
        if not any(word in tag.text for word in ("ITF", "Challenger", "Klasyfikacja")):
            return True
        return False

    tags = []
    for url in urlgen():
        markup = timed_request(url, provider=ForbetOdds.PROVIDER)
        soup = BeautifulSoup(markup, "lxml")
        if validate_soup(soup):
            tags += [tag for tag in soup.find_all("div", class_="event-rate")
                     if tag.attrs["data-gamename"] == "Zwycięzca"]
        print(f"Throttling for {int(THROTTLING_PERIOD * 1000)} ms..")
        sleep(THROTTLING_PERIOD)
        print("Resumed.")

    return tags


class ForbetOdds(Odds):
    """www.iforbet.pl's odds.
    """
    PROVIDER = "ForBET"

    def __init__(self, contender: str, odds: float, event: str) -> None:
        super().__init__(contender, odds)
        self.event = event


def getodds() -> List[ForbetOdds]:
    odds_list = []
    for tag in _get_event_divs():
        contender = tag.attrs["data-outcomename"]
        if "/" in contender:
            continue  # prune doubles
        odds = tag.attrs["data-outcomeodds"]
        event = tag.attrs["data-eventname"]
        odds_list.append(ForbetOdds(contender, float(odds), event))
    print(f"Got total number of {len(odds_list)} {ForbetOdds.PROVIDER} odds.")
    return odds_list


def getpairs() -> List[OddsPair]:
    pairs, odds_list = [], getodds()
    for o in odds_list[:]:
        complement = next((odds for odds in odds_list if o.contender in odds.event
                           and o.contender != odds.contender), None)
        if not complement:
            continue
        else:
            pairs.append(OddsPair(o, complement, o.event))
            odds_list.remove(o)
    print(f"Got {len(pairs)} {ForbetOdds.PROVIDER} odds pairs.")
    return pairs
