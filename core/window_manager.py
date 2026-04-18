import platform
import subprocess
from typing import List, Optional

class WindowManager:
    def __init__(self):
        self.os_type = platform.system()

    def get_active_windows(self) -> List[str]:
        try:
            if self.os_type == "Windows":
                try:
                    import pygetwindow as gw
                    return [w.title for w in gw.getAllWindows() if w.title != ""]
                except ImportError:
                    return ["Error: pygetwindow not installed"]
            
            elif self.os_type == "Darwin":
                script = 'tell application "System Events" to get name of every process whose background only is false'
                output = subprocess.check_output(["osascript", "-e", script]).decode('utf-8')
                return [name.strip() for name in output.split(',') if name.strip()]
            
            elif self.os_type == "Linux":
                try:
                    result = subprocess.run(
                        ["xdotool", "search", "--onlyvisible", "--name", ".*"],
                        capture_output=True, text=True
                    )
                    window_ids = [w for w in result.stdout.strip().split('\n') if w.strip()]
                    windows = []
                    seen = set()
                    for wid in window_ids:
                        try:
                            name = subprocess.run(
                                ["xdotool", "getwindowname", wid],
                                capture_output=True, text=True
                            ).stdout.strip()
                            if name and name not in seen:
                                seen.add(name)
                                windows.append(name)
                        except:
                            pass
                    return sorted(windows) if windows else ["No windows"]
                except FileNotFoundError:
                    return ["Error: xdotool not installed"]
                except Exception as e:
                    print(f"[Error] Linux: {e}")
                    return []
        except Exception as e:
            print(f"[Error] Get windows: {e}")
            return []

    def focus_window_by_title(self, title_substring: str) -> bool:
        try:
            if self.os_type == "Windows":
                try:
                    import pygetwindow as gw
                    for window in gw.getAllWindows():
                        if title_substring.lower() in window.title.lower():
                            window.activate()
                            return True
                except ImportError:
                    pass
                return False

            elif self.os_type == "Linux":
                try:
                    subprocess.run(
                        ["xdotool", "search", "--name", title_substring, "windowactivate"],
                        capture_output=True
                    )
                    return True
                except Exception:
                    return False

            elif self.os_type == "Darwin":
                script = f'tell application "System Events" to set frontmost of process "{title_substring}" to true'
                subprocess.run(["osascript", "-e", script], capture_output=True)
                return True
            
            return False
        except Exception as e:
            print(f"[Error] Focus window: {e}")
            return False

    def check_window_exists(self, title_substring: str) -> bool:
        windows = self.get_active_windows()
        return any(title_substring.lower() in w.lower() for w in windows)