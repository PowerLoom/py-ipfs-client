import sys

from loguru import logger

FORMAT = '{time:MMMM D, YYYY > HH:mm:ss!UTC} | {level} | {message}| {extra}'


logger.add(sys.stdout, level='DEBUG', format=FORMAT)
logger.add(sys.stderr, level='WARNING', format=FORMAT)
logger.add(
    sys.stderr,
    level='ERROR',
    format=FORMAT,
    backtrace=True,
    diagnose=True,
)
