import curses

class TextRenderer:
    def __init__(self, stdscr):
        curses.curs_set(0)
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.log_window = curses.newwin(self.height - 4, self.width, 8, 0)
        self.log_window.scrollok(True)
        self.log_window.idlok(True)
        self.log_window.refresh()
        self.stdscr.nodelay(True)
        self._next_regular_window_line = 0 # The next line to write to in the regular window
        self._next_log_window_line = 0 # The next line to write to in the log window
    
    def clear_line(self, y_pos):
        self.stdscr.addstr(0, y_pos, " " * self.width)
    
    def render(self, message, y_padding=0, y_pos=None):
        y_position = self._next_regular_window_line + y_padding
        if y_pos is not None:
            y_position = y_pos + y_padding
        self.stdscr.addstr(y_position, 0, message)  # Corrected this line
        if y_pos is None:
            self._next_regular_window_line += 1
    
    def log_message(self, message, y_padding=0):
        y_position = self._next_log_window_line + y_padding
        if y_position >= self.height - 4: 
            self.log_window.scroll(1)
            y_position = self.height - 5
        self.log_window.addstr(y_position, 0, message)
        self._next_log_window_line += 1
        self.log_window.refresh()
    
    def draw_horizontal_separator(self, y_pos):
        self.stdscr.addstr(y_pos, 0, "-" * self.width)
    
    def refresh(self):
        self.stdscr.refresh()
        self.log_window.refresh()