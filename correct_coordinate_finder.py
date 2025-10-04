"""
CORRECT Coordinate Finder for Paint MCP Tool
This uses the SAME coordinate system as paint_window.click()
"""

from pywinauto.application import Application
import win32gui
import win32con
from win32api import GetSystemMetrics
import pyautogui
import time

print("="*70)
print("  CORRECT PAINT COORDINATE FINDER")
print("  (Uses window-relative coordinates like MCP tool)")
print("="*70)
print()
print("This will:")
print("1. Open and maximize Paint")
print("2. Track your mouse position in WINDOW-RELATIVE coordinates")
print("3. These coordinates will work directly with the MCP tool")
print()

input("Press Enter to start...")

# Open Paint
print("\nOpening Paint...")
app = Application().start('mspaint.exe')
time.sleep(0.5)

# Get Paint window
paint_window = app.window(class_name='MSPaintApp')

# Position on primary monitor
print("Positioning and maximizing Paint...")
win32gui.SetWindowPos(
    paint_window.handle,
    win32con.HWND_TOP,
    0, 0,
    0, 0,
    win32con.SWP_NOSIZE
)
win32gui.ShowWindow(paint_window.handle, win32con.SW_MAXIMIZE)
time.sleep(1)

# Get Paint window position
window_rect = paint_window.rectangle()
window_left = window_rect.left
window_top = window_rect.top

print(f"Paint window top-left corner: ({window_left}, {window_top})")
print()
print("="*70)
print("  TRACKING WINDOW-RELATIVE COORDINATES")
print("="*70)
print()
print("Move your mouse over the Rectangle tool in Paint")
print("Press Ctrl+C when positioned correctly")
print()

try:
    last_pos = None
    while True:
        # Get absolute screen position
        screen_x, screen_y = pyautogui.position()
        
        # Convert to window-relative coordinates
        window_rel_x = screen_x - window_left
        window_rel_y = screen_y - window_top
        
        current_pos = (window_rel_x, window_rel_y)
        
        if current_pos != last_pos:
            print(f"Screen: ({screen_x:4d}, {screen_y:4d})  |  "
                  f"Window-Relative: ({window_rel_x:4d}, {window_rel_y:4d})  "
                  f"<-- USE THIS", end='\r')
            last_pos = current_pos
        
        time.sleep(0.05)
        
except KeyboardInterrupt:
    screen_x, screen_y = pyautogui.position()
    window_rel_x = screen_x - window_left
    window_rel_y = screen_y - window_top
    
    print("\n\n" + "="*70)
    print("  COORDINATES CAPTURED")
    print("="*70)
    print()
    print(f"Screen coordinates:         ({screen_x}, {screen_y})")
    print(f"Window-relative coordinates: ({window_rel_x}, {window_rel_y})  <-- USE THIS")
    print()
    print("Update your code with:")
    print(f"  rectangle_tool_coords = ({window_rel_x}, {window_rel_y})")
    print()
    print("Or call the function with:")
    print(f"  open_paint_and_select_rectangle({window_rel_x}, {window_rel_y})")
    print()
    print("="*70)
    print()
    
    # Test the click
    test = input("Do you want to TEST this coordinate now? (y/n): ")
    if test.lower() == 'y':
        print(f"\nTesting click at window-relative ({window_rel_x}, {window_rel_y})...")
        paint_window.set_focus()
        time.sleep(0.3)
        
        try:
            paint_window.click(coords=(window_rel_x, window_rel_y))
            print("[OK] Click executed!")
            print("\nCheck if the rectangle tool is selected in Paint!")
            time.sleep(3)
        except Exception as e:
            print(f"[ERROR] Click failed: {e}")
    
    print("\nClosing Paint...")

