import sys
import logging

from ..utils.singleton import Singleton


class Logger(metaclass=Singleton):
    default_config = {
        'name': 'RAG-App',
        'level': 'INFO',
        'format': '[%(asctime)s|%(name)s|%(levelname)s|%(processName)s:%(threadName)s|%(filename)s, '
                  'line %(lineno)s in %(funcName)s] %(message)s',
    }

    def __init__(self,
                 config_to_use: dict = None):

        config = {**Logger.default_config, **(config_to_use or {})}
        self.logger = logging.getLogger(config['name'])

        # Set the root logging level.
        logging_lvl = getattr(logging, config['level'])
        logging.root.setLevel(logging_lvl)

        # Create an handler and configure it.
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging_lvl)
        handler.setFormatter(logging.Formatter(config['format']))

        # Remove all other handlers in the process.
        self.logger.addHandler(handler)

    def get_logger(self) -> logging.Logger:
        return self.logger
