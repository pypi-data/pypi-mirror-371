"""
A terminal clock with retro and plain themes.
"""

import time
import sys
import shutil
from datetime import datetime
from enum import Enum, auto
from typing import List, Tuple
from colorama import init, Fore, Style

init()  # Initialize Colorama for Windows support

class Theme(Enum):
    """Visual themes for the clock."""
    RETRO = auto()
    PLAIN = auto()

class BigFont:
    """Render digits and characters using block elements."""
    
    DIGITS = {
        '0': [
            " █████╗ ",
            "██╔══██╗",
            "██║  ██║",
            "██║  ██║",
            "╚█████╔╝",
            " ╚════╝ "
        ],
        '1': [
            "  ███╗  ",
            " ████║  ",
            "██╔██║  ",
            "╚═╝██║  ",
            "███████╗",
            "╚══════╝"
        ],
        '2': [
            "██████╗ ",
            "╚════██╗",
            "  ███╔═╝",
            "██╔══╝  ",
            "███████╗",
            "╚══════╝"
        ],
        '3': [
            "██████╗ ",
            "╚════██╗",
            " █████╔╝",
            " ╚═══██╗",
            "██████╔╝",
            "╚═════╝ "
        ],
        '4': [
            "  ██╗██╗",
            " ██╔╝██║",
            "██╔╝ ██║",
            "███████║",
            "╚════██║",
            "     ╚═╝"
        ],
        '5': [
            "███████╗",
            "██╔════╝",
            "██████╗ ",
            "╚════██╗",
            "██████╔╝",
            "╚═════╝ "
        ],
        '6': [
            " █████╗ ",
            "██╔═══╝ ",
            "██████╗ ",
            "██╔══██╗",
            "╚█████╔╝",
            " ╚════╝ "
        ],
        '7': [
            "███████╗",
            "╚════██║",
            "    ██╔╝",
            "   ██╔╝ ",
            "  ██╔╝  ",
            "  ╚═╝   "
        ],
        '8': [
            " █████╗ ",
            "██╔══██╗",
            "╚█████╔╝",
            "██╔══██╗",
            "╚█████╔╝",
            " ╚════╝ "
        ],
        '9': [
            " █████╗ ",
            "██╔══██╗",
            "╚██████║",
            " ╚═══██║",
            " █████╔╝",
            " ╚════╝ "
        ],
        ':': [
            "██╗",
            "╚═╝",
            "   ",
            "   ",
            "██╗",
            "╚═╝"
        ],
        ' ': [
            "   ",
            "   ",
            "   ",
            "   ",
            "   ",
            "   "
        ],
        'A': [
            " █████╗ ",
            "██╔══██╗",
            "███████║",
            "██╔══██║",
            "██║  ██║",
            "╚═╝  ╚═╝"
        ],
        'P': [
            "██████╗ ",
            "██╔══██╗",
            "██████╔╝",
            "██╔═══╝ ",
            "██║     ",
            "╚═╝     "
        ],
        'M': [
            "███╗   ███╗",
            "████╗ ████║",
            "██╔████╔██║",
            "██║╚██╔╝██║",
            "██║ ╚═╝ ██║",
            "╚═╝     ╚═╝"
        ]
    }

    @classmethod
    def render_big_text(cls, text: str) -> List[str]:
        """Convert text to big font representation."""
        lines = [""] * 6
        for char in text:
            char_pattern = cls.DIGITS.get(char.upper(), cls.DIGITS[' '])
            for i in range(6):
                lines[i] += char_pattern[i] + "  "
        return lines

class ColorClock:
    def __init__(
        self,
        theme: Theme = Theme.RETRO,
        military_time: bool = False,
        show_date: bool = True,
        show_milliseconds: bool = False,
        big_font: bool = True,
        blink_separators: bool = True,
    ):
        """
        Initialize a terminal clock.
        """
        self.theme = theme
        self.military_time = military_time
        self.show_date = show_date
        self.show_milliseconds = show_milliseconds
        self.big_font = big_font
        self.blink_separators = blink_separators
        self.running = False
        self._separator_visible = True
        self._terminal_width = shutil.get_terminal_size().columns

    def _get_theme_colors(self) -> Tuple[str, str]:
        """Return color palette for the current theme."""
        themes = {
            Theme.RETRO: (Fore.GREEN, Fore.YELLOW),
            Theme.PLAIN: (Fore.WHITE, Fore.LIGHTBLACK_EX)
        }
        return themes.get(self.theme, (Fore.WHITE, Fore.LIGHTBLACK_EX))

    def _apply_theme(self, text_lines: List[str], element_type: str = "time") -> List[str]:
        """Apply styling based on theme."""
        time_color, date_color = self._get_theme_colors()
        styled_lines = []
        
        for line in text_lines:
            if element_type == "time":
                styled_lines.append(f"{time_color}{Style.BRIGHT}{line}{Style.RESET_ALL}")
            elif element_type == "date":
                styled_lines.append(f"{date_color}{line}{Style.RESET_ALL}")
            else:
                styled_lines.append(f"{time_color}{line}{Style.RESET_ALL}")
        
        return styled_lines

    def _format_time_string(self, now: datetime) -> str:
        """Format the time string for display."""
        time_format = "%H:%M:%S" if self.military_time else "%I:%M:%S %p"
        
        if self.show_milliseconds:
            time_format = time_format.replace("%S", "%S.%f")[:-3]
        
        time_str = now.strftime(time_format)
        
        if self.blink_separators and not self._separator_visible:
            time_str = time_str.replace(':', ' ')
        
        return time_str

    def _center_lines(self, lines: List[str]) -> List[str]:
        """Center multiple lines of text in the terminal."""
        return [line.center(self._terminal_width) for line in lines]

    def _create_display_output(self, now: datetime) -> List[str]:
        """Create the complete display output with styling."""
        output_lines = []
        
        # Add date header
        if self.show_date:
            date_str = now.strftime("%A, %B %d, %Y")
            date_line = f" {date_str} ".center(self._terminal_width, '─')
            styled_date = self._apply_theme([date_line], 'date')
            output_lines.extend(["\n", styled_date[0], "\n"])
        
        # Create time display
        time_str = self._format_time_string(now)
        
        if self.big_font:
            big_time_lines = BigFont.render_big_text(time_str)
            styled_time = self._apply_theme(big_time_lines, 'time')
            centered_time = self._center_lines(styled_time)
            output_lines.extend(centered_time)
        else:
            centered_time = f" {time_str} ".center(self._terminal_width)
            styled_time = self._apply_theme([centered_time], 'time')
            output_lines.append(styled_time[0])
        
        # Add footer
        footer = "PRESS CTRL+C TO EXIT".center(self._terminal_width)
        output_lines.extend(["\n" * 2, f"{Fore.LIGHTBLACK_EX}{footer}{Style.RESET_ALL}"])
        
        return output_lines

    def display(self):
        """Display the continuously updating clock."""
        self.running = True
        last_second = -1
        
        try:
            while self.running:
                now = datetime.now()
                current_second = now.second
                
                if not self.show_milliseconds and current_second == last_second:
                    time.sleep(0.05)
                    continue
                
                last_second = current_second
                self._separator_visible = not self._separator_visible if self.blink_separators else True
                
                # Handle terminal resize
                try:
                    self._terminal_width = shutil.get_terminal_size().columns
                except:
                    pass
                
                output_lines = self._create_display_output(now)
                
                sys.stdout.write("\033[2J\033[H") 
                sys.stdout.write("\n".join(output_lines))
                sys.stdout.flush()
                
                if self.show_milliseconds:
                    time.sleep(0.05)
                else:
                    time.sleep(1.0 - (time.time() % 1.0))
                    
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stop the clock."""
        self.running = False
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()

def quick_start(theme: str = "retro", **kwargs):
    """
    Start the clock.
    """
    theme_mapping = {
        'retro': Theme.RETRO,
        'plain': Theme.PLAIN
    }
    
    clock = ColorClock(
        theme=theme_mapping.get(theme.lower(), Theme.RETRO),
        **kwargs
    )
    
    clock.display()

if __name__ == "__main__":
    quick_start(
        theme="retro",
        big_font=True,
        show_date=True,
        blink_separators=True,
        military_time=False
    )