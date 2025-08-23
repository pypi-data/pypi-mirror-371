import logging

logger = logging.getLogger("rule34html")
if not logger.handlers:
    # Default: no handlers, library stays quiet unless user configures logging
    handler = logging.NullHandler()
    logger.addHandler(handler)
