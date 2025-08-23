# Terminal Clock

A stylish terminal clock with retro and plain themes featuring big font display.

## Installation

```bash
pip install ASDFGH
Quick Start
bash
# Run with default settings (retro theme, big font)
python -m clock
Basic Usage
python
from clock import quick_start

# Start with retro theme
quick_start()

# Start with plain theme
quick_start(theme="plain")
Advanced Usage
python
from clock import ColorClock, Theme

# Custom configuration
clock = ColorClock(
    theme=Theme.RETRO,          # Theme.RETRO or Theme.PLAIN
    military_time=False,        # 12-hour format (False) or 24-hour (True)
    show_date=True,             # Show date header
    show_milliseconds=False,    # Show milliseconds
    big_font=True,              # Use big block font
    blink_separators=True,      # Blinking colon separators
)

clock.display()  # Press CTRL+C to exit
Features
🎨 Dual Themes: Retro (green) and Plain (white) themes

🔢 Big Font: Large block-style digits for easy reading

📅 Date Display: Optional date header

⏰ Time Formats: 12-hour and 24-hour format support

✨ Visual Effects: Optional blinking colon separators

🎯 Centered Display: Automatically centers in terminal

Options
Parameter           Default             Description
theme	            Theme.RETRO	        Visual theme (RETRO/PLAIN)
military_time	    False	            24-hour format when True
show_date	        True	            Show date header
show_milliseconds	False	            Show milliseconds
big_font	        True	            Use big block font
blink_separators	True	            Blink colon separators


Exit
Press CTRL+C to gracefully exit the clock.