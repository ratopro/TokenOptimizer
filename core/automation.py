import time
import platform
import pyperclip
import pyautogui
from typing import Literal

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05

class AutomationController:
    def __init__(self):
        self.injection_method: Literal["paste", "typewrite"] = "paste"
        self.send_enter_after: bool = True

    def set_method(self, method: str):
        if method in ["paste", "typewrite"]:
            self.injection_method = method

    def inject_text(self, text: str) -> bool:
        if not text:
            return False
        try:
            pyautogui.typewrite(text, interval=0.005)
            if self.send_enter_after:
                time.sleep(0.1)
                pyautogui.press("enter")
            return True
        except Exception as e:
            print(f"[Error] Injection failed: {e}")
            return False

    def _inject_via_paste(self) -> bool:
        try:
            if platform.system() == "Darwin":
                pyautogui.hotkey("command", "v")
            else:
                pyautogui.hotkey("ctrl", "v")
            
            if self.send_enter_after:
                time.sleep(0.1)
                pyautogui.press("enter")
            return True
        except Exception as e:
            print(f"[Error] Paste failed: {e}")
            return False

    def _inject_via_typewrite(self, text: str) -> bool:
        try:
            pyautogui.typewrite(text, interval=0.01)
            
            if self.send_enter_after:
                time.sleep(0.1)
                pyautogui.press("enter")
            return True
        except Exception as e:
            print(f"[Error] Typewrite failed: {e}")
            return False

    def simulate_enter(self):
        pyautogui.press("enter")

    def cleanup(self):
        pyperclip.copy("")