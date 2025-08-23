from logging import Logger

logger = Logger("utils_logger")

SILENCE = True

def print(*args):
    if not SILENCE:
        logger.info(" ".join(map(str, args)))