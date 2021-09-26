"""

    scrape
    ~~~~~~
    Scrape polish tennis bookies.

    @author: z33k

"""


class OddsUnavailableError(ValueError):
    """Raised when even though scraping works, odds are still unavailable.
    """