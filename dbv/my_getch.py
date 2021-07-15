
import termios


EOT = "\x04"
SIGINT = "\x03"
SIGTSTP = "\x1a"


class MyGetch:
    """Gets a single character from standard input without echo to screen"""

    def __init__(self) -> None:
        try:
            import msvcrt
        except ImportError:
            import sys
            import tty

    def _getch(self) -> None:
        try:
            import msvcrt
            return msvcrt.getch()
        except ImportError:
            import sys
            import tty


            # Puts the terminal into cbreak mode, meaning keys aren't echoed to the screen
            # and can be read immediately without input buffering.
            fd = sys.stdin.fileno()
            tattr = tty.tcgetattr(fd)

            try:
                tty.setcbreak(sys.stdin.fileno())
                ch = sys.stdin.read(1)
            finally: # restores terminal to default behavior
                # FIXME: TCSADRAIN vs TCSANOW ? Adrain might remove race conditions?
                termios.tcsetattr(fd, termios.TCSADRAIN, tattr) 
            return ch

    def __call__(self) -> bytes:
        ch = self._getch()

        if ch == SIGINT or ch == SIGTSTP:
            raise KeyboardInterrupt
        elif ch == EOT:
            raise EOFError

        return ch


    def _getch_unix(self) -> bytes:
        pass
