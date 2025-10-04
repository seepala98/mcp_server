import pyautogui
import time

# Update this to only show in terminal when i click the mouse after i click stop this script
def on_click(x, y, button, pressed):
    if pressed:
        print(f"Mouse clicked at ({x}, {y}) with {button}")

if __name__ == "__main__":
    from pynput import mouse
    try:
        with mouse.Listener(on_click=on_click) as listener:
            listener.join()
    # when i press ctrl+c in terminal, it should stop listening to mouse events
    except KeyboardInterrupt:
        print("Stopped listening to mouse events.")