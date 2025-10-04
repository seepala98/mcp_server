"""
⚠️ WARNING: This tool may give INCORRECT coordinates!
Use 'correct_coordinate_finder.py' instead for accurate window-relative coordinates.

Quick Coordinate Finder - Simple mouse position tracker (SCREEN COORDINATES)
Note: pywinauto uses WINDOW-RELATIVE coordinates, not screen coordinates!
"""

import pyautogui
import time

print("╔═══════════════════════════════════════════════════════════╗")
print("║        Quick Mouse Position Finder                       ║")
print("║     ⚠️  WARNING: May give wrong coordinates!             ║")
print("║     Use 'correct_coordinate_finder.py' instead!          ║")
print("╚═══════════════════════════════════════════════════════════╝")
print("\n⚠️  This tool shows SCREEN coordinates.")
print("⚠️  But MCP tool needs WINDOW-RELATIVE coordinates!")
print()
print("Recommended: Run 'python correct_coordinate_finder.py' instead")
print()
cont = input("Continue anyway? (y/n): ")
if cont.lower() != 'y':
    print("Good choice! Run: python correct_coordinate_finder.py")
    exit()

print("\nInstructions:")
print("1. Open Paint manually")
print("2. Maximize it on your primary monitor")
print("3. Move your mouse over the Rectangle tool")
print("4. Look at the coordinates displayed below")
print("5. Press Ctrl+C when you have the right position\n")

input("Press Enter to start tracking...")

print("\nTracking SCREEN coordinates (may not work in MCP tool)...\n")

try:
    last_pos = None
    while True:
        x, y = pyautogui.position()
        if (x, y) != last_pos:
            print(f"SCREEN X: {x:4d}  Y: {y:4d}  -->  coords=({x}, {y})", end='\r')
            last_pos = (x, y)
        time.sleep(0.05)
except KeyboardInterrupt:
    x, y = pyautogui.position()
    print(f"\n\n{'='*60}")
    print(f"✓ Screen coordinates captured: ({x}, {y})")
    print(f"\n⚠️  IMPORTANT: These are SCREEN coordinates!")
    print(f"⚠️  They might NOT work with paint_window.click()")
    print(f"\n✅ For correct coordinates, run:")
    print(f"   python correct_coordinate_finder.py")
    print(f"{'='*60}\n")

