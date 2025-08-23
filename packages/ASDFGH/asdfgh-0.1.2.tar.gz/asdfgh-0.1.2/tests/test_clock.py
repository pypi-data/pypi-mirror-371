# test_clock.py
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from clock import ColorClock, Theme, BigFont

def test_big_font_rendering():
    """Test that BigFont renders text correctly."""
    result = BigFont.render_big_text("12:34")
    assert len(result) == 6  # Should have 6 lines
    assert all(len(line) > 0 for line in result)  # All lines should have content

def test_theme_enum():
    """Test that Theme enum works correctly."""
    assert Theme.RETRO != Theme.PLAIN
    assert isinstance(Theme.RETRO, Theme)

def test_clock_initialization():
    """Test that ColorClock initializes with correct defaults."""
    clock = ColorClock()
    assert clock.theme == Theme.RETRO
    assert clock.military_time == False
    assert clock.show_date == True
    assert clock.big_font == True

def test_time_formatting():
    """Test time formatting with different settings."""
    clock = ColorClock(military_time=False)
    test_time = datetime(2023, 12, 25, 14, 30, 45)
    
    time_str = clock._format_time_string(test_time)
    assert "PM" in time_str or "AM" in time_str
    
    clock.military_time = True
    military_time_str = clock._format_time_string(test_time)
    assert "14:" in military_time_str

def test_blink_separators():
    """Test separator blinking functionality."""
    clock = ColorClock(blink_separators=True)
    test_time = datetime(2023, 12, 25, 12, 30, 45)
    
    # Test with separator visible
    clock._separator_visible = True
    visible_str = clock._format_time_string(test_time)
    assert ":" in visible_str
    
    # Test with separator hidden
    clock._separator_visible = False
    hidden_str = clock._format_time_string(test_time)
    assert ":" not in hidden_str

@patch('clock.shutil.get_terminal_size')
@patch('clock.datetime')
def test_display_output(mock_datetime, mock_terminal_size):
    """Test display output creation."""
    # Mock terminal size
    mock_terminal_size.return_value.columns = 80
    
    # Mock current time
    test_time = datetime(2023, 12, 25, 12, 30, 45)
    mock_datetime.now.return_value = test_time
    
    clock = ColorClock()
    output = clock._create_display_output(test_time)
    
    assert len(output) > 0
    assert any("EXIT" in line for line in output)  # Should contain exit message

def test_quick_start():
    """Test quick_start function with different themes."""
    from clock import quick_start
    
    # This just tests that the function can be called without errors
    # We'll mock the actual display method to avoid infinite loop
    with patch.object(ColorClock, 'display'):
        # Should not raise any errors
        quick_start(theme="retro")
        quick_start(theme="plain")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])