import logging


class Colors:
    """Class with a few pre-defined ANSI colors for cleaner output.
    The list was extracted from:
    https://gist.github.com/rene-d/9e584a7dd2935d0f461904b9f2950007
    """
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    LIGHT_GRAY = "\033[0;37m"
    DARK_GRAY = "\033[1;30m"
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class KernelLogger:
    def __init__(self, prefix=''):
        self.prefix = prefix
        self.log_level = logging.DEBUG

    def log(self, msg, msg_log_level=logging.INFO):
        """Log to the output which is visible to the user.
        """
        if msg_log_level >= self.log_level:
            if msg_log_level == logging.DEBUG:
                print(self._get_log_start(), f"{Colors.LIGHT_GRAY} {msg} {Colors.ENDC}")
            elif msg_log_level == logging.WARNING:
                print(self._get_log_start(), f"{Colors.YELLOW} {msg} {Colors.ENDC}")
            elif msg_log_level == logging.ERROR:
                print(self._get_log_start(), f"{Colors.RED} {msg} {Colors.ENDC}")
            else:
                print(self._get_log_start(), msg)

    def _get_log_start(self):
        """Get the initial part of the log.
        """
        return f"{Colors.BLUE} {Colors.BOLD} {self.prefix} {Colors.ENDC} {Colors.ENDC}"
