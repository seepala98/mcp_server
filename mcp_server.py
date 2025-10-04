# basic import 
from mcp.server.fastmcp import FastMCP, Image
from mcp.server.fastmcp.prompts import base
from mcp.types import TextContent
from mcp import types
from PIL import Image as PILImage
import math
import sys
from pywinauto.application import Application
import win32gui
import win32con
import time
from win32api import GetSystemMetrics

# instantiate an MCP server client
mcp = FastMCP("Calculator")

# Global variable for Paint application
paint_app = None

# DEFINE TOOLS

#addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    print("CALLED: add(a: int, b: int) -> int:")
    return int(a + b)

@mcp.tool()
def add_list(l: list) -> int:
    """Add all numbers in a list"""
    print("CALLED: add(l: list) -> int:")
    return sum(l)

# subtraction tool
@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    print("CALLED: subtract(a: int, b: int) -> int:")
    return int(a - b)

# multiplication tool
@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    print("CALLED: multiply(a: int, b: int) -> int:")
    return int(a * b)

#  division tool
@mcp.tool() 
def divide(a: int, b: int) -> float:
    """Divide two numbers"""
    print("CALLED: divide(a: int, b: int) -> float:")
    return float(a / b)

# power tool
@mcp.tool()
def power(a: int, b: int) -> int:
    """Power of two numbers"""
    print("CALLED: power(a: int, b: int) -> int:")
    return int(a ** b)

# square root tool
@mcp.tool()
def sqrt(a: int) -> float:
    """Square root of a number"""
    print("CALLED: sqrt(a: int) -> float:")
    return float(a ** 0.5)

# cube root tool
@mcp.tool()
def cbrt(a: int) -> float:
    """Cube root of a number"""
    print("CALLED: cbrt(a: int) -> float:")
    return float(a ** (1/3))

# factorial tool
@mcp.tool()
def factorial(a: int) -> int:
    """factorial of a number"""
    print("CALLED: factorial(a: int) -> int:")
    return int(math.factorial(a))

# log tool
@mcp.tool()
def log(a: int) -> float:
    """log of a number"""
    print("CALLED: log(a: int) -> float:")
    return float(math.log(a))

# remainder tool
@mcp.tool()
def remainder(a: int, b: int) -> int:
    """remainder of two numbers divison"""
    print("CALLED: remainder(a: int, b: int) -> int:")
    return int(a % b)

# sin tool
@mcp.tool()
def sin(a: int) -> float:
    """sin of a number"""
    print("CALLED: sin(a: int) -> float:")
    return float(math.sin(a))

# cos tool
@mcp.tool()
def cos(a: int) -> float:
    """cos of a number"""
    print("CALLED: cos(a: int) -> float:")
    return float(math.cos(a))

# tan tool
@mcp.tool()
def tan(a: int) -> float:
    """tan of a number"""
    print("CALLED: tan(a: int) -> float:")
    return float(math.tan(a))

# mine tool
@mcp.tool()
def mine(a: int, b: int) -> int:
    """special mining tool"""
    print("CALLED: mine(a: int, b: int) -> int:")
    return int(a - b - b)

@mcp.tool()
def create_thumbnail(image_path: str) -> Image:
    """Create a thumbnail from an image"""
    print("CALLED: create_thumbnail(image_path: str) -> Image:")
    img = PILImage.open(image_path)
    img.thumbnail((100, 100))
    return Image(data=img.tobytes(), format="png")

@mcp.tool()
def strings_to_chars_to_int(string: str) -> list[int]:
    """Return the ASCII values of the characters in a word"""
    print("CALLED: strings_to_chars_to_int(string: str) -> list[int]:")
    return [int(ord(char)) for char in string]

@mcp.tool()
def int_list_to_exponential_sum(int_list: list) -> float:
    """Return sum of exponentials of numbers in a list"""
    print("CALLED: int_list_to_exponential_sum(int_list: list) -> float:")
    return sum(math.exp(i) for i in int_list)

@mcp.tool()
def fibonacci_numbers(n: int) -> list:
    """Return the first n Fibonacci Numbers"""
    print("CALLED: fibonacci_numbers(n: int) -> list:")
    if n <= 0:
        return []
    fib_sequence = [0, 1]
    for _ in range(2, n):
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    return fib_sequence[:n]


@mcp.tool()
async def open_paint_and_select_rectangle(rect_tool_x: int, rect_tool_y: int) -> dict:
    """Open Paint on primary monitor, maximize it, and click the rectangle tool at specified coordinates.
    Call this ONCE before drawing. Example: open_paint_and_select_rectangle(658, 103)"""
    global paint_app
    
    print("\n" + "="*60)
    print(f"OPEN_PAINT_AND_SELECT_RECTANGLE CALLED")
    print(f"Rectangle tool coordinates: ({rect_tool_x}, {rect_tool_y})")
    print("="*60)
    
    try:
        # Check if Paint is already open
        if paint_app is not None:
            print("[OK] Paint is already open")
            
            # Still select the rectangle tool
            paint_window = paint_app.window(class_name='MSPaintApp')
            paint_window.set_focus()
            time.sleep(0.3)
            
            print(f"Clicking rectangle tool at ({rect_tool_x}, {rect_tool_y})...")
            try:
                paint_window.click(coords=(rect_tool_x, rect_tool_y))
                time.sleep(0.5)
                print("[OK] Rectangle tool selected")
            except:
                paint_window.click_input(coords=(rect_tool_x, rect_tool_y))
                time.sleep(0.5)
                print("[OK] Rectangle tool selected")
            
            primary_width = GetSystemMetrics(0)
            primary_height = GetSystemMetrics(1)
            
            return {
                "content": [
                    TextContent(
                        type="text",
                        text=f"Paint already open. Rectangle tool selected at ({rect_tool_x},{rect_tool_y}). Monitor: {primary_width}x{primary_height}"
                    )
                ]
            }
        
        # Open Paint
        print("Step 1: Starting Paint application...")
        paint_app = Application().start('mspaint.exe')
        time.sleep(0.5)
        print("[OK] Paint started")
        
        # Get Paint window
        print("Step 2: Getting Paint window...")
        paint_window = paint_app.window(class_name='MSPaintApp')
        print("[OK] Got Paint window")
        
        # Get monitor dimensions
        primary_width = GetSystemMetrics(0)
        primary_height = GetSystemMetrics(1)
        print(f"Step 3: Monitor dimensions: {primary_width}x{primary_height}")
        
        # Position on primary monitor
        print("Step 4: Positioning on primary monitor...")
        win32gui.SetWindowPos(
            paint_window.handle,
            win32con.HWND_TOP,
            0, 0,
            0, 0,
            win32con.SWP_NOSIZE
        )
        print("[OK] Positioned")
        
        # Maximize
        print("Step 5: Maximizing Paint...")
        win32gui.ShowWindow(paint_window.handle, win32con.SW_MAXIMIZE)
        time.sleep(0.8)
        print("[OK] Maximized")
        
        # Focus Paint window
        print("Step 6: Focusing Paint window...")
        paint_window.set_focus()
        time.sleep(0.3)
        print("[OK] Focused")
        
        # Click rectangle tool
        print(f"Step 7: Clicking rectangle tool at ({rect_tool_x}, {rect_tool_y})...")
        print("  NOTE: If tool doesn't get selected, run 'python test_paint_click.py'")
        try:
            paint_window.click(coords=(rect_tool_x, rect_tool_y))
            time.sleep(0.5)
            print("[OK] Rectangle tool clicked (using .click())")
        except Exception as e:
            print(f"[WARN] .click() failed, trying .click_input()...")
            paint_window.click_input(coords=(rect_tool_x, rect_tool_y))
            time.sleep(0.5)
            print("[OK] Rectangle tool clicked (using .click_input())")
        
        print("\n[SUCCESS] Paint opened and rectangle tool selected!")
        print("="*60 + "\n")
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Paint opened on primary monitor ({primary_width}x{primary_height}), maximized, and rectangle tool selected at ({rect_tool_x},{rect_tool_y})"
                )
            ]
        }
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(f"\n[ERROR] {error_msg}")
        print("="*60 + "\n")
        import traceback
        traceback.print_exc()
        return {
            "content": [
                TextContent(
                    type="text",
                    text=error_msg
                )
            ]
        }

@mcp.tool()
async def draw_rectangle(x1: int, y1: int, x2: int, y2: int) -> dict:
    """Draw a rectangle in Paint from (x1,y1) to (x2,y2). 
    Must call open_paint_and_select_rectangle first to select the rectangle tool."""
    global paint_app
    
    print("\n" + "="*60)
    print(f"DRAW_RECTANGLE CALLED: ({x1},{y1}) to ({x2},{y2})")
    print("="*60)
    
    try:
        # Check if Paint is open
        if not paint_app:
            print("[ERROR] Paint not opened!")
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="Paint is not open. Call open_paint_and_select_rectangle first."
                    )
                ]
            }
        
        print("[OK] Paint app is open")
        
        # Get Paint window
        print("Step 1: Getting Paint window...")
        paint_window = paint_app.window(class_name='MSPaintApp')
        print("[OK] Got Paint window")
        
        # Ensure Paint window is active
        print("Step 2: Ensuring Paint is focused...")
        if not paint_window.has_focus():
            paint_window.set_focus()
            time.sleep(0.3)
        print("[OK] Paint focused")
        
        # Get canvas
        print("Step 3: Getting canvas...")
        canvas = paint_window.child_window(class_name='MSPaintView')
        print("[OK] Got canvas")
        
        # Draw rectangle with mouse drag
        print(f"\nStep 4: Drawing rectangle from ({x1},{y1}) to ({x2},{y2})...")
        
        print(f"  a) Pressing mouse at ({x1},{y1})")
        canvas.press_mouse_input(coords=(x1, y1))
        time.sleep(0.15)
        print(f"  [OK] Mouse pressed")
        
        print(f"  b) Dragging to ({x2},{y2})")
        canvas.move_mouse_input(coords=(x2, y2))
        time.sleep(0.15)
        print(f"  [OK] Mouse dragged")
        
        print(f"  c) Releasing mouse")
        canvas.release_mouse_input(coords=(x2, y2))
        time.sleep(0.2)
        print(f"  [OK] Mouse released")
        
        print("\n[SUCCESS] Rectangle drawn!")
        print("="*60 + "\n")
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Rectangle drawn from ({x1},{y1}) to ({x2},{y2})"
                )
            ]
        }
    except Exception as e:
        error_msg = f"Error drawing rectangle: {str(e)}"
        print(f"\n[ERROR] {error_msg}")
        print("="*60 + "\n")
        import traceback
        traceback.print_exc()
        return {
            "content": [
                TextContent(
                    type="text",
                    text=error_msg
                )
            ]
        }

@mcp.tool()
async def add_text_in_paint(text: str) -> dict:
    """Add text in Paint"""
    global paint_app
    try:
        if not paint_app:
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="Paint is not open. Please call open_paint first."
                    )
                ]
            }
        
        # Get the Paint window
        paint_window = paint_app.window(class_name='MSPaintApp')
        
        # Ensure Paint window is active
        if not paint_window.has_focus():
            paint_window.set_focus()
            time.sleep(0.5)
        
        # Click on the Rectangle tool
        paint_window.click_input(coords=(528, 92))
        time.sleep(0.5)
        
        # Get the canvas area
        canvas = paint_window.child_window(class_name='MSPaintView')
        
        # Select text tool using keyboard shortcuts
        paint_window.type_keys('t')
        time.sleep(0.1)
        paint_window.type_keys('x')
        time.sleep(0.5)
        
        # Click where to start typing
        canvas.click_input(coords=(810, 533))
        time.sleep(0.5)
        
        # Type the text passed from client
        paint_window.type_keys(text)
        time.sleep(0.5)
        
        # Click to exit text mode
        canvas.click_input(coords=(1050, 800))
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Text:'{text}' added successfully"
                )
            ]
        }
    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )
            ]
        }

# Removed old open_paint() function - replaced with open_paint_and_select_rectangle()
# DEFINE RESOURCES

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    print("CALLED: get_greeting(name: str) -> str:")
    return f"Hello, {name}!"


# DEFINE AVAILABLE PROMPTS
@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"
    print("CALLED: review_code(code: str) -> str:")


@mcp.prompt()
def debug_error(error: str) -> list[base.Message]:
    return [
        base.UserMessage("I'm seeing this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]

if __name__ == "__main__":
    # Check if running with mcp dev command
    print("STARTING THE SERVER AT AMAZING LOCATION")
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()  # Run without transport for dev server
    else:
        mcp.run(transport="stdio")  # Run with stdio for direct execution
