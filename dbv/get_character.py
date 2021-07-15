
EOT = "\x04"  # CTRL + D
SIGINT = "\x03"  # CTRL + C
SIGTSTP = "\x1a"  # CTRL + Z


class MyGetch:
    """Gets a single character from standard input without echo to screen"""

    def _getch(self) -> None:
        """Operating sytem aware implementation of getch() like function"""
        try:
            import msvcrt
            return msvcrt.getch().decode()
        except ImportError:
            import sys
            import termios
            import tty

            # Puts the terminal into cbreak mode, meaning keys aren't echoed to the screen
            # and can be read immediately without input buffering.
            fd = sys.stdin.fileno()
            tattr = tty.tcgetattr(fd)

            try:
                tty.setcbreak(sys.stdin.fileno())
                ch = sys.stdin.read(1)
            finally:  # restores terminal to default behavior
                # FIXME: TCSADRAIN vs TCSANOW ? Adrain might remove race conditions?
                termios.tcsetattr(fd, termios.TCSADRAIN, tattr)
            return ch

    def __call__(self) -> bytes:
        """Returns a single character from stdin using _getch()"""
        ch = self._getch()

        if ch == SIGINT or ch == SIGTSTP:
            raise KeyboardInterrupt
        elif ch == EOT:
            raise EOFError

        return ch
