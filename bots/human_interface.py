import pyautogui
from pyclick import HumanClicker


class HumanInterface(HumanClicker):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_mouse_position():
        return pyautogui.position()

    @staticmethod
    def get_screen_size():
        return pyautogui.size()

    def set_fail_safe(self, fail_safe_bool: bool):
        pyautogui.FAILSAFE = fail_safe_bool
