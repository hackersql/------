import logging
from xpath_blindeye.retrieve import retrieve

if __name__ == "__main__":
    logging.basicConfig(level="WARN")
    logger = logging.getLogger("xpath-blindeye")
    logger.setLevel("INFO")
    retrieve()
