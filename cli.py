import sys

if sys.platform == 'darwin' or sys.platform[:3] == 'lin':
    import curses
elif sys.platform[:3] == 'win':
    import msvcrt
    import os


class CliBaseClass:
    """This class is used to display text in the command line and react to user
    input."""

    def __init__(self):
        self.actions = dict()
        self.status = list()

    def add_action(self, command, fn, *args, **kwargs):
        """Adds an action that can be triggered by user input.

        Args:
            command (string): The key the user needs to press to trigger the
                action. If the keyword argument `toolbar` is set to True, the
                first character of `command` is used as key but the whole string
                is displayed in the toolbar.
            fn (callable): Function executed when the command is recognised.
            *args: Arguments passed to `fn`.
            **kwargs: Arguments passed to `fn`. Argument `toolbar` is removed
                from kwargs before they are passed to the function.

        Examples:
            >>> self.add_action('start', lambda: self.display("hello world!"),
            ...                 toolbar=True)
            Will add the action bound to the key `s` and with the title
            "(s)tart" in the toolbar.
            >>> self.add_action('KEY_UP', lambda: self.display, "hello world!",
            ...                 style='underline')
            Will display "hello world" underlined when the up arrow key is
            pressed.
        """
        if kwargs.get('toolbar', False):
            kwargs.pop('toolbar')
            self._add_toolbar(command, fn, *args, **kwargs)
        else:
            self._add_action(command, fn, *args, **kwargs)

    def _add_toolbar(self, command, fn, *args, **kwargs):
        """Add command to toolbar. See `add_action`."""
        key = command[0]
        self.actions[key] = {
            'cmdstr': '({}){}'.format(command[0], command[1:]),
            'toolbar': True,
            'function': fn,
            'args': args,
            'kwargs': kwargs
        }

    def _add_action(self, command, fn, *args, **kwargs):
        """Add command. See `add_action`."""
        self.actions[command] = {
            'cmdstr': command,
            'function': fn,
            'args': args,
            'kwargs': kwargs
        }

    def display(self, *args, **kwargs):
        """Displays a string of text in the command line interface."""
        raise NotImplemented()

    def display_toolbar(self):
        """Displays all commands registered in the toolbar."""
        for _, action in self.actions.items():
            if not action.get('toolbar', False):
                continue
            self.display(action['cmdstr'], style="underline", end='')
            self.display(' ', end='')
        self.display()

    def getkey(self, *args, **kwargs):
        """Returns the key character pressed by the user. Blocking."""
        raise NotImplemented()

    def handle_action(self):
        """Handles an action based on the user input. Blocks until a key is
        pressed."""
        key = self.getkey()
        if key in self.actions:
            action = self.actions[key]
            action['function'](
                *action.get('args', []), **action.get('kwargs', {}))

    def wait_for_input(self):
        """Blocks until a key is pressed by the user."""
        self.getkey()

    def add_status(self, *args, **kwargs):
        """Adds a status string to the status board."""
        self.status.append({'args': args, 'kwargs': kwargs})

    def clear_status(self):
        """Clears the status board."""
        self.status.clear()

    def display_status(self):
        """Displays every status string stored in the status board."""
        for status in self.status:
            self.display(*status['args'], **status['kwargs'])

    def clear(self):
        """Clears the interface of all text."""
        raise NotImplemented()

    @staticmethod
    def close():
        """Performs the closing operations needed to restore the terminal to
        its original settings."""
        pass


class CliCurses(CliBaseClass):
    """Command line interface implemented with curses. Not supported on
    Windows. See CliWindows."""

    STYLES = {
        'normal': curses.A_NORMAL,
        'underline': curses.A_UNDERLINE,
        'bold': curses.A_BOLD
    }
    COLORS = {
        'default': 0, 'red': 1, 'yellow': 2
    }

    def __init__(self):
        super().__init__()
        # Get terminal
        self.stdscr = curses.initscr()
        # Init colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)     # red
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # yellow
        # No visual echo when a key is pressed.
        curses.noecho()
        # React without the need to press the enter key
        curses.cbreak()
        # Handle special keys
        self.stdscr.keypad(True)
        # Set scrolling ok
        self.stdscr.idlok(True)
        self.stdscr.scrollok(True)

    @staticmethod
    def close():
        curses.nocbreak()
        curses.echo()
        # Restore terminal to previous settings
        curses.endwin()

    def getkey(self):
        return self.stdscr.getkey()

    def display(self, string='', end="\n", style='normal', color='default'):
        self.stdscr.addstr("{}{}".format(string, end),
                           CliCurses.STYLES[style]|
                           curses.color_pair(CliCurses.COLORS[color]))
        self.stdscr.refresh()

    def clear(self):
        self.stdscr.clear()


class CliWindows(CliBaseClass):
    KEYS = {
        122: 'KEY_UP',
        115: 'KEY_DOWN',
        113: 'KEY_LEFT',
        100: 'KEY_RIGHT',
    }

    def getkey(self, *args, **kwargs):
        return CliWindows.KEYS[msvcrt.getwch()[0]]

    def display(self, string='', *args, **kwargs):
        print(string, end=kwargs.get('end', '\n\r'))

    def clear(self, *args, **kwargs):
        os.system('cls')


def get_cli():
    """Returns the correct Cli implementation for the current operating system."""
    # return CliWindows()
    if sys.platform == 'darwin' or sys.platform[:3] == 'lin':
        return CliCurses()
    elif sys.platform[:3] == 'win':
        return CliWindows()
