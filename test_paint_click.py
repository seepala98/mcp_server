"""
Simple Paint Rectangle Tool Coordinate Tester
This will help you find the EXACT coordinates for the rectangle tool
"""

from pywinauto.application import Application
import win32gui
import win32con
from win32api import GetSystemMetrics
import time

print("="*70)
print("  PAINT RECTANGLE TOOL COORDINATE FINDER")
print("="*70)
print()
print("This script will:")
print("1. Open Paint and maximize it")
print("2. Wait 3 seconds")
print("3. Test clicking at coordinates (658, 103)")
print("4. Wait 5 seconds for you to verify")
print()
print("Watch carefully if the rectangle tool gets selected!")
print()

input("Press Enter to start...")

# Start Paint
print("\nOpening Paint...")
app = Application().start('mspaint.exe')
time.sleep(1)

# Get Paint window
paint_window = app.window(class_name='MSPaintApp')

# Position on primary monitor
print("Positioning on primary monitor...")
win32gui.SetWindowPos(
    paint_window.handle,
    win32con.HWND_TOP,
    0, 0,
    0, 0,
    win32con.SWP_NOSIZE
)

# Maximize
print("Maximizing Paint...")
win32gui.ShowWindow(paint_window.handle, win32con.SW_MAXIMIZE)
time.sleep(1)

# Get monitor dimensions
width = GetSystemMetrics(0)
height = GetSystemMetrics(1)
print(f"Monitor dimensions: {width}x{height}")

print("\nPaint is now open and maximized.")
print("Waiting 3 seconds before clicking...")
time.sleep(3)

# Test click at current coordinates
test_coords = (658, 103)
print(f"\nAttempting to click at {test_coords}...")
try:
    paint_window.click(coords=test_coords)
    print("[OK] Click executed")
except Exception as e:
    print(f"[ERROR] Click failed: {e}")
    print("Trying click_input instead...")
    paint_window.click_input(coords=test_coords)
    print("[OK] Click executed with click_input")

print("\n" + "="*70)
print("  VERIFICATION TIME - 5 SECONDS")
print("="*70)
print()
print("Look at Paint now!")
print("Questions to check:")
print("  1. Is the RECTANGLE tool selected/highlighted?")
print("  2. Or did it click somewhere else?")
print("  3. Where is the mouse cursor now?")
print()

for i in range(5, 0, -1):
    print(f"  Closing in {i} seconds...", end='\r')
    time.sleep(1)

print("\n\nIf rectangle tool WAS selected: Coordinates (658, 103) are CORRECT")
print("If rectangle tool was NOT selected: You need to find correct coordinates")
print()
print("To find correct coordinates, run:")
print("  python quick_coordinate_finder.py")
print()
print("="*70)

