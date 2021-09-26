"""

    scrape.betx.py
    ~~~~~~~~~~~~~~
    Scrape https://ebetx.pl for tennis odds.

    @author: z33k

"""
import requests

URL = "https://sportapis.ebetx.pl/SportOfferApi/api/sport/offer/v2/sports/offer"

POSTDATA = {
    "Offset": 0,
    "Limit": 50,
    "SportIds": [389],
    "CategoryIds": [],
    "LeagueIds": [],
    "DateFrom": "2021-09-26T21:25:18.482Z",  # ought to be replaced with datetime.now() probably
    "DateTo": "2022-07-22T22:00:00.482Z"
}

r = requests.post(URL, json=POSTDATA)
data = r.json()["Response"][0]
tournaments = [t for item in data["Categories"] for t in item["Leagues"]]
matches = [item for t in tournaments for item in t["Matches"]]

# TODO: object encapsulating one of 'matches' thats takes and parses its ["BasicOffer"]["Odds"]
#  element for odds. The contender data sits in a match element's ["TeamHome"] and ["TeamAway"]
#  elements
