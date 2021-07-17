from contextlib import contextmanager
from typing import ContextManager

EOT = "\x04"  # CTRL + D
SIGINT = "\x03"  # CTRL + C
SIGTSTP = "\x1a"  # CTRL + Z

try:
    import msvcrt

    @contextmanager
    def cbreak() -> ContextManager:
        """Microsoft cbreak()."""
        yield

    def _getch() -> str:
        """Microsoft getch()."""
        return msvcrt.getch().decode()
except ImportError:
    import sys
    import termios
    import tty

    # Puts the terminal into cbreak mode, meaning keys aren't echoed to the screen
    # and can be read immediately without input buffering.

    @contextmanager
    def cbreak() -> ContextManager:
        """Unix cbreak()."""
        fd = sys.stdin.fileno()
        tattr = tty.tcgetattr(fd)

        try:
            tty.setcbreak(sys.stdin.fileno())
            yield
        finally:  # restores terminal to default behavior
            # FIXME: TCSADRAIN vs TCSANOW ? Adrain might remove race conditions?
            termios.tcsetattr(fd, termios.TCSADRAIN, tattr)

    def _getch() -> str:
        """Unix getch()."""
        return sys.stdin.read(1)


def get_char() -> str:
    """Get a single character from standard input without echo to screen"""
    ch = _getch()

    if ch == SIGINT or ch == SIGTSTP:
        raise KeyboardInterrupt
    elif ch == EOT:
        raise EOFError

    return ch
