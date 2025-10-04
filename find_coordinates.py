"""
Helper script to find correct coordinates for Paint controls
Run this script and it will help you identify the right coordinates
"""

import pyautogui
import time
from pywinauto.application import Application
from pywinauto import Desktop
import win32gui
import win32con
from win32api import GetSystemMetrics

def get_mouse_position():
    """Get current mouse position - move mouse to element and run this"""
    print("\n=== Mouse Position Finder ===")
    print("Move your mouse over the element you want to click")
    print("Press Ctrl+C to stop")
    print("\nWaiting 3 seconds before starting...\n")
    time.sleep(3)
    
    try:
        while True:
            x, y = pyautogui.position()
            print(f"Current mouse position: ({x}, {y})    ", end='\r')
            time.sleep(0.1)
    except KeyboardInterrupt:
        print(f"\n\nFinal position: ({x}, {y})")
        return x, y

def inspect_paint_controls():
    """Inspect Paint window structure to find controls"""
    print("\n=== Paint Window Inspector ===")
    print("Opening Paint...\n")
    
    try:
        # Start Paint
        app = Application().start('mspaint.exe')
        time.sleep(1)
        
        # Get Paint window
        paint_window = app.window(class_name='MSPaintApp')
        
        # Get primary monitor dimensions
        primary_width = GetSystemMetrics(0)
        primary_height = GetSystemMetrics(1)
        
        # Position on primary monitor
        win32gui.SetWindowPos(
            paint_window.handle,
            win32con.HWND_TOP,
            0, 0,
            0, 0,
            win32con.SWP_NOSIZE
        )
        
        # Maximize
        win32gui.ShowWindow(paint_window.handle, win32con.SW_MAXIMIZE)
        time.sleep(1)
        
        print("Paint opened and maximized on primary monitor")
        print(f"Monitor dimensions: {primary_width}x{primary_height}\n")
        
        # Print control structure
        print("=== Paint Window Controls ===")
        paint_window.print_control_identifiers()
        
        print("\n\n=== Looking for Rectangle Tool ===")
        # Try to find rectangle-related controls
        try:
            controls = paint_window.descendants()
            for i, ctrl in enumerate(controls):
                try:
                    name = ctrl.window_text()
                    class_name = ctrl.class_name()
                    rect = ctrl.rectangle()
                    
                    # Look for controls that might be the rectangle tool
                    if any(keyword in name.lower() for keyword in ['rectangle', 'rect', 'shape']) or \
                       any(keyword in class_name.lower() for keyword in ['button', 'tool']):
                        print(f"\nControl #{i}:")
                        print(f"  Name: {name}")
                        print(f"  Class: {class_name}")
                        print(f"  Position: ({rect.left}, {rect.top}) to ({rect.right}, {rect.bottom})")
                        print(f"  Center: ({(rect.left + rect.right)//2}, {(rect.top + rect.bottom)//2})")
                except Exception as e:
                    continue
        except Exception as e:
            print(f"Error finding controls: {e}")
        
        print("\n\nNow use Method 2 to manually find coordinates...")
        print("The Paint window will stay open for 30 seconds.")
        print("Move your mouse over the Rectangle tool and note the coordinates from the title bar or use Method 2.")
        time.sleep(30)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def find_coordinates_with_screenshot():
    """Take a screenshot and show coordinates"""
    print("\n=== Screenshot Coordinate Finder ===")
    print("This will take a screenshot and help you find coordinates\n")
    
    try:
        # Take screenshot
        screenshot = pyautogui.screenshot()
        width, height = screenshot.size
        print(f"Screen size: {width}x{height}")
        
        # Save screenshot
        screenshot_path = "paint_screenshot.png"
        screenshot.save(screenshot_path)
        print(f"\nScreenshot saved as: {screenshot_path}")
        print("Open the screenshot, find the rectangle tool, and note its pixel coordinates")
        print("Tip: You can use an image viewer with coordinate display or MS Paint itself!")
        
    except Exception as e:
        print(f"Error: {e}")

def test_click_coordinates(x, y):
    """Test if clicking at given coordinates works"""
    print(f"\n=== Testing Click at ({x}, {y}) ===")
    print("Opening Paint...\n")
    
    try:
        # Start Paint
        app = Application().start('mspaint.exe')
        time.sleep(1)
        
        # Get Paint window
        paint_window = app.window(class_name='MSPaintApp')
        
        # Position and maximize
        win32gui.SetWindowPos(
            paint_window.handle,
            win32con.HWND_TOP,
            0, 0,
            0, 0,
            win32con.SWP_NOSIZE
        )
        win32gui.ShowWindow(paint_window.handle, win32con.SW_MAXIMIZE)
        time.sleep(1)
        
        print("Paint opened. Testing click...")
        paint_window.set_focus()
        time.sleep(0.5)
        
        # Test click
        print(f"Clicking at ({x}, {y})...")
        paint_window.click(coords=(x, y))
        
        print("\nClick executed! Check if the rectangle tool is selected.")
        print("The Paint window will stay open for 10 seconds for you to verify.")
        time.sleep(10)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║     Paint Coordinate Finder - Choose a Method            ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print("\n1. Mouse Position Finder (Real-time mouse tracking)")
    print("2. Inspect Paint Controls (Show all clickable elements)")
    print("3. Screenshot Method (Take screenshot for analysis)")
    print("4. Test Specific Coordinates (Test a coordinate)")
    print("5. Exit")
    
    while True:
        print("\n" + "="*60)
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == "1":
            get_mouse_position()
        elif choice == "2":
            inspect_paint_controls()
        elif choice == "3":
            find_coordinates_with_screenshot()
        elif choice == "4":
            x = int(input("Enter X coordinate: "))
            y = int(input("Enter Y coordinate: "))
            test_click_coordinates(x, y)
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter 1-5.")

if __name__ == "__main__":
    main()

