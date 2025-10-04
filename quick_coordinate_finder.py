"""
Quick Coordinate Finder - Simple mouse position tracker
Run this and move your mouse over the rectangle tool to get coordinates
"""

import pyautogui
import time

print("╔═══════════════════════════════════════════════════════════╗")
print("║        Quick Mouse Position Finder                       ║")
print("╚═══════════════════════════════════════════════════════════╝")
print("\nInstructions:")
print("1. Open Paint manually")
print("2. Maximize it on your primary monitor")
print("3. Move your mouse over the Rectangle tool")
print("4. Look at the coordinates displayed below")
print("5. Press Ctrl+C when you have the right position\n")

input("Press Enter to start tracking...")

print("\nTracking mouse position... (Press Ctrl+C to stop)\n")

try:
    last_pos = None
    while True:
        x, y = pyautogui.position()
        if (x, y) != last_pos:
            print(f"X: {x:4d}  Y: {y:4d}  -->  coords=({x}, {y})", end='\r')
            last_pos = (x, y)
        time.sleep(0.05)
except KeyboardInterrupt:
    x, y = pyautogui.position()
    print(f"\n\n{'='*60}")
    print(f"✓ Final coordinates captured: ({x}, {y})")
    print(f"\nUpdate your code with:")
    print(f"  rectangle_tool_coords = ({x}, {y})")
    print(f"{'='*60}\n")

