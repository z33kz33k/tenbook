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

# from scrape.forbet import getpairs
# pairs = getpairs()
# print(len(pairs))

from pprint import pprint
from scrape import betclic, betx, betfan, etoto, ewinner, forbet

pairs = [
    *betclic.getpairs(),
    # *betx.getpairs(),
    # *betfan.getpairs(),
    # *etoto.getpairs(),
    # *ewinner.getpairs(),
    # *forbet.getpairs(),
]
pprint(sorted([p for p in pairs if "Ruud" in p.nameparts], key=lambda p: p.spread))

