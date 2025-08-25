from logngraph.log.levels import *
from datetime import datetime
import sys
import threading

__all__ = [
    "get_logger",
    "Logger",
]

_loggers = {}
_lock = threading.Lock()

def get_logger(name: str, filename: str = None, level: int = INFO) -> "Logger":
    """Get or create a named logger instance."""
    with _lock:
        if name not in _loggers:
            _loggers[name] = Logger(name, filename, level)
        return _loggers[name]


class Logger:
    _file_handles = {}
    _file_locks = {}
    _stdout_lock = threading.Lock()

    def __init__(self, name: str, filename: str = None, level: int = INFO):
        """
        Logger class

        :param name: Name of the logger
        :param filename: Filename of the log file (optional)
        :param level: Logging level (can be changed using Logger.set_level)
        """
        self.name = name
        self.filename = filename
        self.file = open(filename, "w") if filename else None
        self.stdout = sys.stdout
        self.level = level

        if filename:
            if filename not in Logger._file_handles:
                f = open(filename, 'a')
                Logger._file_handles[filename] = f
                Logger._file_locks[filename] = threading.Lock()

    @property
    def dtstr(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")[:-3]

    def set_level(self, level: int) -> bool:
        if 0 <= level <= 6:
            self.level = level
            return True
        return False

    def print(self, text: str) -> None:
        if self.filename:
            with Logger._file_locks[self.filename]:
                Logger._file_handles[self.filename].write(text)
                Logger._file_handles[self.filename].flush()

        with Logger._stdout_lock:
            self.stdout.write(text)
            self.stdout.flush()

    def trace(self, msg: str) -> None:
        if self.level <= TRACE:
            log = f"\x1b[38;5;123mTRACE: {self.dtstr}: [{self.name}]: {msg}\x1b[0m\n"
            self.print(log)

    def debug(self, msg: str) -> None:
        if self.level <= DEBUG:
            log = f"\x1b[38;5;11mDEBUG: {self.dtstr}: [{self.name}]: {msg}\x1b[0m\n"
            self.print(log)

    def info(self, msg: str) -> None:
        if self.level <= INFO:
            log = f"\x1b[38;5;251mINFO:  {self.dtstr}: [{self.name}]: {msg}\x1b[0m\n"
            self.print(log)

    def warn(self, msg: str) -> None:
        if self.level <= WARNING:
            log = f"\x1b[38;5;208m\x1b[1mWARN:  {self.dtstr}: [{self.name}]: {msg}\x1b[0m\n"
            self.print(log)

    def error(self, msg: str) -> None:
        if self.level <= ERROR:
            log = f"\x1b[38;5;196m\x1b[1mERROR: {self.dtstr}: [{self.name}]: {msg}\x1b[0m\n"
            self.print(log)

    def fatal(self, msg: str) -> None:
        if self.level <= FATAL:
            log = f"\x1b[38;5;124m\x1b[1mFATAL: {self.dtstr}: [{self.name}]: {msg}\x1b[0m\n"
            self.print(log)

    def close(self) -> None:
        """Close the file handle if this is the last logger using it"""
        if self.filename:
            with _lock:
                # Count how many loggers are using this file
                users = sum(1 for logger in _loggers.values()
                          if logger.filename == self.filename)

                if users <= 1:
                    if self.filename in Logger._file_handles:
                        Logger._file_handles[self.filename].close()
                        del Logger._file_handles[self.filename]
                        del Logger._file_locks[self.filename]

    def __del__(self) -> None:
        self.close()


if __name__ == "__main__":
    # Testing field
    logger = Logger(__name__, "test.log", TRACE)
    logger.trace("trace")
    logger.debug("debug")
    logger.info("info")
    logger.warn("warn")
    logger.error("error")
    logger.fatal("fatal")

