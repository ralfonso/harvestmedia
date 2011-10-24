from blinker import signal
import logging

logger = logging.getLogger('harvestmedia')

class Signals:
    def __init__(self):
        self._signals = {}

    def add_signal(self, name):
        self._signals[name] = signal(name)

    def connect(self, name, func):
        logger.debug('connecting %s to signal %s' % (func, name))
        self._signals[name].connect(func)

    def send(self, name, *args, **kwargs):
        logger.debug('sending signal %s' % name)
        self._signals[name].send(*args, **kwargs)

signals = Signals()
