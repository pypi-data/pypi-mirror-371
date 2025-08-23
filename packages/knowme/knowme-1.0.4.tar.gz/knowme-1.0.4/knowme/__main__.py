import os
import shutil
import re
from . import ascii
from . import system_info
from .utils import colorize

def get_terminal_width():
    """Get terminal width, default to 80 if unable to determine."""
    try:
        return shutil.get_terminal_size().columns
    except:
        return 80

def strip_ansi_codes(text):
    """Remove ANSI color codes to get actual text length."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def center_logo_vertically(logo_lines, info_lines):
    """Center logo vertically relative to info lines."""
    logo_height = len(logo_lines)
    info_height = len(info_lines)
    
    if logo_height < info_height:
        # Add empty lines to center the logo
        padding_top = (info_height - logo_height) // 2
        padding_bottom = info_height - logo_height - padding_top
        
        centered_logo = [''] * padding_top + logo_lines + [''] * padding_bottom
        return centered_logo
    
    return logo_lines

def main():
    """
    Main function to fetch info and print it in a perfectly aligned two-column layout.
    """
    # Get terminal width for better alignment
    terminal_width = get_terminal_width()
    
    logo_str = ascii.get_os_logo()
    info_dict = system_info.get_all_system_info()

    # Split logo and info into lines for processing
    logo_lines = logo_str.strip().split('\n')
    info_lines = []

    # Format the information dictionary into "Key: Value" strings
    for key, value in info_dict.items():
        # The 'Condition' value is already colorized in system_info.py
        if key == "Condition":
            colored_value = str(value)
        else:
            colored_value = colorize(str(value))
        
        # Handle multi-line values (like Disk and Network info)
        if '\n' in str(value):
            parts = str(value).split('\n')
            # Colorize the first part differently if it's not pre-colored
            first_part_colored = colorize(parts[0]) if key != "Condition" else parts[0]
            info_lines.append(f"{key}: {first_part_colored}")

            for part in parts[1:]:
                # Indent and colorize subsequent lines
                info_lines.append(f"   {colorize(part.strip())}")
        else:
            info_lines.append(f"{key}: {colored_value}")

    # Center logo vertically relative to info
    logo_lines = center_logo_vertically(logo_lines, info_lines)

    # Calculate optimal spacing
    max_logo_width = max(len(strip_ansi_codes(line)) for line in logo_lines) if logo_lines else 0
    
    # Adaptive gutter width based on terminal size
    if terminal_width >= 120:
        gutter_width = 6
    elif terminal_width >= 100:
        gutter_width = 4
    else:
        gutter_width = 2

    # Ensure we have enough lines to display
    num_display_lines = max(len(logo_lines), len(info_lines))

    # Print header with some spacing
    print()
    
    # Combine logo and info lines side-by-side with perfect alignment
    for i in range(num_display_lines):
        # Get the logo line (with colors)
        logo_line = logo_lines[i] if i < len(logo_lines) else ""
        
        # Get the plain logo line for length calculation (without ANSI codes)
        plain_logo_line = strip_ansi_codes(logo_line)
        
        # Get the info part
        info_part = info_lines[i] if i < len(info_lines) else ""

        # Calculate precise padding based on the actual visible length
        padding_needed = max_logo_width - len(plain_logo_line) + gutter_width
        padding = " " * max(0, padding_needed)

        # Print the perfectly aligned line
        print(f"{logo_line}{padding}{info_part}")
    
    # Print footer with some spacing
    print()

if __name__ == "__main__":
    main()
