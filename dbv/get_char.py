EOT = "\x04"  # CTRL + D
SIGINT = "\x03"  # CTRL + C
SIGTSTP = "\x1a"  # CTRL + Z

try:
    import msvcrt

    def _getch() -> str:
        """Get character on Windows systems."""
        return msvcrt.getch().decode()


except ImportError:
    import sys
    import termios
    import tty

    def _getch() -> str:
        """
        Get character on Unix systems.

        Puts the terminal into cbreak mode, meaning keys aren't echoed to the screen
        and can be read immediately without input buffering.
        """
        fd = sys.stdin.fileno()
        tattr = tty.tcgetattr(fd)

        try:
            tty.setcbreak(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:  # restores terminal to default behavior
            # FIXME: TCSADRAIN vs TCSANOW ? Adrain might remove race conditions?
            termios.tcsetattr(fd, termios.TCSADRAIN, tattr)
        return ch


def get_char() -> str:
    """Get a single character from standard input without echo to screen."""
    ch = _getch()

    if ch == SIGINT or ch == SIGTSTP:
        raise KeyboardInterrupt
    elif ch == EOT:
        raise EOFError

    return ch
