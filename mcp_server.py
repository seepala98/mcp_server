# mcp_server.py

# basic import 
from mcp.server.fastmcp import FastMCP, Image
from mcp.server.fastmcp.prompts import base
from mcp.types import TextContent
from mcp import types
from PIL import Image as PILImage
import math
import sys
import time
from pywinauto.application import Application
import win32gui
import win32con
from win32api import GetSystemMetrics
import pyautogui

# instantiate an MCP server client
mcp = FastMCP("Calculator")

# Global variable for Paint application
paint_app = None

# ------------------------------------------------
# MATH TOOLS
# ------------------------------------------------
@mcp.tool()
def add(a: int, b: int) -> int: return int(a + b)

@mcp.tool()
def add_list(l: list) -> int: return sum(l)

@mcp.tool()
def subtract(a: int, b: int) -> int: return int(a - b)

@mcp.tool()
def multiply(a: int, b: int) -> int: return int(a * b)

@mcp.tool()
def divide(a: int, b: int) -> float: return float(a / b)

@mcp.tool()
def power(a: int, b: int) -> int: return int(a ** b)

@mcp.tool()
def sqrt(a: int) -> float: return float(a ** 0.5)

@mcp.tool()
def cbrt(a: int) -> float: return float(a ** (1/3))

@mcp.tool()
def factorial(a: int) -> int: return int(math.factorial(a))

@mcp.tool()
def log(a: int) -> float: return float(math.log(a))

@mcp.tool()
def remainder(a: int, b: int) -> int: return int(a % b)

@mcp.tool()
def sin(a: int) -> float: return float(math.sin(a))

@mcp.tool()
def cos(a: int) -> float: return float(math.cos(a))

@mcp.tool()
def tan(a: int) -> float: return float(math.tan(a))

@mcp.tool()
def mine(a: int, b: int) -> int: return int(a - b - b)

# ------------------------------------------------
# IMAGE / STRING TOOLS
# ------------------------------------------------
@mcp.tool()
def create_thumbnail(image_path: str) -> Image:
    img = PILImage.open(image_path)
    img.thumbnail((100, 100))
    return Image(data=img.tobytes(), format="png")

@mcp.tool()
def strings_to_chars_to_int(string: str) -> list[int]:
    return [ord(char) for char in string]

@mcp.tool()
def int_list_to_exponential_sum(int_list: list) -> float:
    return sum(math.exp(i) for i in int_list)

@mcp.tool()
def fibonacci_numbers(n: int) -> list:
    if n <= 0:
        return []
    fib_sequence = [0, 1]
    for _ in range(2, n):
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    return fib_sequence[:n]

# ------------------------------------------------
# PAINT AUTOMATION TOOLS
# ------------------------------------------------
@mcp.tool()
async def open_paint_and_select_rectangle(rect_tool_x: int, rect_tool_y: int) -> dict:
    """Open Paint, maximize, and select rectangle tool correctly."""
    global paint_app
    try:
        if paint_app is None:
            paint_app = Application().start('mspaint.exe')
            time.sleep(1)

            # Get Paint window
            paint_window = paint_app.window(title_re=".*Paint.*")
            win32gui.SetWindowPos(paint_window.handle, win32con.HWND_TOP, 0, 0, 0, 0, win32con.SWP_NOSIZE)
            win32gui.ShowWindow(paint_window.handle, win32con.SW_MAXIMIZE)
            time.sleep(1)

        # Click rectangle shape dropdown if necessary (adjust coordinates!)
        # pyautogui.click(rect_tool_x, rect_tool_y) may not always select rectangle
        # Sometimes you need to click twice or drag to select correct shape
        pyautogui.moveTo(rect_tool_x, rect_tool_y)
        pyautogui.click()
        time.sleep(0.2)
        pyautogui.click()  # double-click to ensure rectangle selected
        time.sleep(0.2)

        # Optional: click inside canvas to ensure focus
        pyautogui.click(400, 400)

        primary_width = GetSystemMetrics(0)
        primary_height = GetSystemMetrics(1)

        return {
            "content": [TextContent(
                type="text",
                text=f"Paint opened ({primary_width}x{primary_height}) and rectangle tool selected at ({rect_tool_x},{rect_tool_y})"
            )]
        }
    except Exception as e:
        return {"content": [TextContent(type="text", text=f"Error: {str(e)}")]}


@mcp.tool()
async def draw_rectangle(x1: int, y1: int, x2: int, y2: int) -> dict:
    """Draw a rectangle in Paint using pyautogui drag."""
    try:
        pyautogui.moveTo(x1, y1)
        pyautogui.mouseDown()
        pyautogui.moveTo(x2, y2, duration=0.5)
        pyautogui.mouseUp()
        return {"content": [TextContent(type="text", text=f"Rectangle drawn from ({x1},{y1}) to ({x2},{y2})")]}
    except Exception as e:
        return {"content": [TextContent(type="text", text=f"Error: {str(e)}")]}

# @mcp.tool()
# async def add_text_in_paint(text: str, text_tool_x: int, text_tool_y: int, text_box_x1: int, text_box_y1: int, text_box_x2: int, text_box_y2: int) -> dict:
#     """Add text in Paint. Click text tool, create text box, and paste text.
#     Example: add_text_in_paint|FINAL_ANSWER: 42|347|98|400|400|800|500"""
#     print("\n" + "="*60)
#     print(f"ADD_TEXT_IN_PAINT CALLED")
#     print(f"Text: {text}")
#     print(f"Text tool: ({text_tool_x}, {text_tool_y})")
#     print(f"Text box: ({text_box_x1},{text_box_y1}) to ({text_box_x2},{text_box_y2})")
#     print("="*60)
    
#     try:
#         # Step 1: Click Text Tool
#         print(f"Step 1: Clicking text tool at ({text_tool_x}, {text_tool_y})...")
#         pyautogui.click(text_tool_x, text_tool_y)
#         time.sleep(0.8)
#         print("[OK] Text tool clicked")

#         # Step 2: Create text box by dragging
#         print(f"\nStep 2: Creating text box from ({text_box_x1},{text_box_y1}) to ({text_box_x2},{text_box_y2})...")
        
#         print(f"  a) Moving to start position...")
#         pyautogui.moveTo(text_box_x1, text_box_y1)
#         time.sleep(0.2)
#         print(f"  [OK] At start position")
        
#         print(f"  b) Pressing left mouse button...")
#         pyautogui.mouseDown(button='left')
#         time.sleep(0.2)
#         print(f"  [OK] Mouse button pressed")
        
#         print(f"  c) Dragging to end position...")
#         pyautogui.moveTo(text_box_x2, text_box_y2, duration=0.5)
#         time.sleep(0.2)
#         print(f"  [OK] Dragged to end position")
        
#         print(f"  d) Releasing mouse button...")
#         pyautogui.mouseUp(button='left')
#         time.sleep(0.8)
#         print(f"  [OK] Mouse released - text box should be created")

#         # Step 3: Type text directly (more reliable than clipboard)
#         print(f"\nStep 3: Typing text...")
#         pyautogui.typewrite(text, interval=0.05)
#         time.sleep(0.5)
#         print(f"[OK] Text typed: {text}")
        
#         # Alternative: Use clipboard if typewrite fails
#         # import pyperclip
#         # pyperclip.copy(text)
#         # pyautogui.hotkey('ctrl', 'v')

#         print("\n[SUCCESS] Text added to Paint!")
#         print("="*60 + "\n")
        
#         return {
#             "content": [TextContent(type="text", text=f"Text '{text}' added in Paint at ({text_box_x1},{text_box_y1})")]
#         }

@mcp.tool()
async def add_text_in_paint(text: str) -> dict:
    """Add text in Paint at a fixed canvas location"""
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

        # Select the Text tool (shortcut 'T')
        paint_window.type_keys('t')
        time.sleep(0.5)

        # Click on the canvas to create a text box
        # Adjust coordinates as needed for your screen resolution
        canvas_x, canvas_y = 500, 500
        paint_window.click_input(coords=(canvas_x, canvas_y))
        time.sleep(0.5)

        # Type the text
        paint_window.type_keys(text, pause=0.05)
        time.sleep(0.5)

        # Click outside the text box to finish editing
        paint_window.click_input(coords=(canvas_x + 200, canvas_y + 200))
        time.sleep(0.2)

        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Text:'{text}' added successfully at ({canvas_x},{canvas_y})"
                )
            ]
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )
            ]
        }


# ------------------------------------------------
# RESOURCES & PROMPTS
# ------------------------------------------------
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    return f"Hello, {name}!"

@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"

@mcp.prompt()
def debug_error(error: str) -> list[base.Message]:
    return [
        base.UserMessage("I'm seeing this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]

# ------------------------------------------------
if __name__ == "__main__":
    print("STARTING THE SERVER...")
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()  
    else:
        mcp.run(transport="stdio")
