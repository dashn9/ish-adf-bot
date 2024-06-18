import ctypes
import pyautogui
import random
import time
from multiprocessing import Value

from selenium.common import StaleElementReferenceException
from selenium.webdriver.common.by import By

from browsers.browser_interface import BrowserInterface
from constants import bot_constants
from humanbehaviourmechanics.human_movements import HumanMovements


class HumanBehaviourReveries:
    active_on_mouse_movement = Value(ctypes.c_int, -1)

    def __init__(self):
        pass

    def move_mouse_to_fool_exit_point(self):
        """
        Attempts to move mouse towards the browser exit button
        :return: Boolean
        """
        if HumanBehaviourReveries.active_on_mouse_movement.value < 0:
            HumanBehaviourReveries.active_on_mouse_movement.value = self.bot_process_id
            self.bring_window_to_front()
            self.simulate_human_mouse_move_behavior_to_point(
                random.randint(0, bot_constants.SCREEN_WIDTH), 4
            )
            time.sleep(0.5)
            HumanBehaviourReveries.active_on_mouse_movement.value = (
                -self.bot_process_id if self.bot_process_id != 0 else -500
            )
            return True
        return False

    def move_mouse_to_random_area_on_screen(
        self,
        bounds: dict = {
            "x": 0,
            "y": 0,
            "width": bot_constants.SCREEN_WIDTH,
            "height": bot_constants.SCREEN_HEIGHT,
        },
    ):
        if HumanBehaviourReveries.active_on_mouse_movement.value < 0:
            HumanBehaviourReveries.active_on_mouse_movement.value = self.bot_process_id
            self.bring_window_to_front()
            self.simulate_human_mouse_move_behavior_to_area(
                bounds["x"],
                bounds["y"],
                bounds["width"],
                bounds["height"],
                x_coordinates_offset_percentage=random.randint(0, 100),
                y_coordinates_offset_percentage=random.randint(0, 100),
                max_overshoot=35,
                probability_of_overshoot=round(random.random(), 2),
            )
            time.sleep(0.5)
            HumanBehaviourReveries.active_on_mouse_movement.value = (
                -self.bot_process_id if self.bot_process_id != 0 else -500
            )

    def open_link_in_elements(self, elements):
        links_to_follow = []
        for el in elements:
            for link in el.find_elements(By.TAG_NAME, "a"):
                link_children = link.find_elements(By.CSS_SELECTOR, "*")
                if len(link_children) >= 1:
                    for link_child in link_children:
                        links_to_follow.append(link_child)
                else:
                    links_to_follow.append(link)
        if (
            HumanBehaviourReveries.active_on_mouse_movement.value < 0
            and len(links_to_follow) >= 1
        ):
            HumanBehaviourReveries.active_on_mouse_movement.value = self.bot_process_id
            print(
                f"Bot Process Id {self.bot_process_id} <:::> Attempting To Open A Link In Related Articles"
            )
            self.bring_window_to_front()
            link_to_follow = links_to_follow[
                random.randint(0, len(links_to_follow) - 1)
            ]
            self.move_pointing_device_to_element(link_to_follow)
            time.sleep(random.uniform(0.2, 0.8))
            if self.has_touch:
                time.sleep(random.uniform(0.3, 0.5))
                try:
                    element_location_and_dimensions = (
                        self.get_element_location_window_offset(link_to_follow)
                    )
                    # Do click continually until page remained unchanged after click
                    self.touch.tap(
                        element_location_and_dimensions["x_offset"]
                        + random.uniform(0, link_to_follow.rect["width"]),
                        element_location_and_dimensions["y_offset"]
                        + random.uniform(0, link_to_follow.rect["height"]),
                    )
                    while self.revert_to_main_page():
                        self.touch.tap(
                            element_location_and_dimensions["x_offset"]
                            + random.uniform(0, link_to_follow.rect["width"]),
                            element_location_and_dimensions["y_offset"]
                            + random.uniform(0, link_to_follow.rect["height"]),
                        )
                except StaleElementReferenceException:
                    print(
                        f"Bot Process Id {self.bot_process_id} <:::> An attempt to click on a link in the related "
                        f"article section cause a StaleElementReference error. This is most likely the result of "
                        f"external interaction with the browser that forced a new tab to open without script "
                        f"awareness"
                    )
            else:
                # Do click continually until page remained unchanged after click
                pyautogui.click()
                while self.revert_to_main_page():
                    pyautogui.click()
            print(
                f"Bot Process Id {self.bot_process_id} <:::> Done Attempting To Open A Link In Related Articles"
            )
            time.sleep(0.3)
            HumanBehaviourReveries.active_on_mouse_movement.value = (
                -self.bot_process_id if self.bot_process_id != 0 else -500
            )
            return True
        return False
