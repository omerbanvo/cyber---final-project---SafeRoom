import logging


def setup_logging(level: int = logging.INFO)-> None:
    logging.basicConfig(
        level = level, 
        format= "%(asctime)s [%(levelname)s] %(threadName)s: %(message)s", 
        datefmt= "%H:%M:%S",
    )