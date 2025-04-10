import sys
from functools import lru_cache

from loguru import logger

# Format string for log messages
FORMAT = '{time:MMMM D, YYYY > HH:mm:ss!UTC} | {level} | Message: {message} | {extra}'


def create_level_filter(level):
    """
    Create a filter function for a specific log level.
    """
    return lambda record: record['level'].name == level


@lru_cache(maxsize=None)
def get_logger():
    """
    Configure and return the logger instance.
    This function is cached, so it will only configure the logger once.
    """
    # Force remove all handlers
    new_logger = logger.bind()
    new_logger.configure(handlers=[])
    new_logger.remove()
    # Configure file logging

    logger.add(sys.stdout, level='TRACE', format=FORMAT, filter=create_level_filter('TRACE'))
    logger.add(sys.stdout, level='DEBUG', format=FORMAT, filter=create_level_filter('DEBUG'))

    logger.add(sys.stdout, level='INFO', format=FORMAT, filter=create_level_filter('INFO'))
    logger.add(sys.stdout, level='SUCCESS', format=FORMAT, filter=create_level_filter('SUCCESS'))

    logger.add(sys.stderr, level='WARNING', format=FORMAT, filter=create_level_filter('WARNING'))
    logger.add(sys.stderr, level='ERROR', format=FORMAT, filter=create_level_filter('ERROR'))
    logger.add(sys.stderr, level='CRITICAL', format=FORMAT, filter=create_level_filter('CRITICAL'))

    return new_logger


# Usage
default_logger = get_logger()
