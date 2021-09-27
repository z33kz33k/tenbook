"""

    run.py
    ~~~~~~
    Run the scripts.

    @author: z33k

"""
from pprint import pprint
#
# from scrape import betclic, betfan
#
# betclic_odds = betclic.getodds()
# betfan_odds = betfan.getodds()
# print()
# print("Betclic odds:")
# print("=============")
# pprint(betclic_odds)
# print("BETFAN odds:")
# print("============")
# pprint(betfan_odds)

from scrape import pairs_to_odds
from scrape.betclic import getpairs
odds = pairs_to_odds(getpairs())
pprint(odds)

