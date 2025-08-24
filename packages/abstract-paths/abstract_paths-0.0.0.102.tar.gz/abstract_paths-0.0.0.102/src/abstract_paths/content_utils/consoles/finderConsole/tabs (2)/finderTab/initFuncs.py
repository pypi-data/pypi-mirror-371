

from .functions import (append_log, open_all_hits, open_one, populate_results, start_search)

def initFuncs(self):
    try:
        for f in (append_log, open_all_hits, open_one, populate_results, start_search):
            setattr(self, f.__name__, f)
    except Exception as e:
        logger.info(f"{e}")
    return self
