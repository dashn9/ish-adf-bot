import ctypes
import pyautogui
import random
import time
import asyncio
from multiprocessing import Value

from selenium.webdriver.common.by import By

from nodriver import Element as WebElement

from bots import utils as global_utils
from constants import bot_constants, device_constants
from constants.keyboard_keys import Keys as K_Keys
from humanbehaviourmechanics.human_behaviour_reveries import HumanBehaviourReveries
from humanbehaviourmechanics.human_movements import HumanMovements
from humanbehaviourmechanics.smart_ads_interactions import SmartAdsInteractions


class SmartHumanReader(HumanMovements, SmartAdsInteractions, HumanBehaviourReveries):
    active_on_mouse_movement = Value(ctypes.c_int, -1)

    def __init__(self, reading_speed=900, no_of_clicks=0):
        self.reading_speed = reading_speed
        HumanMovements.__init__(self)
        SmartAdsInteractions.__init__(self, no_of_clicks)
        HumanBehaviourReveries.__init__(self)

    async def read_by_mode(
        self,
        html_web_element: WebElement,
        px_to_adjust_by,
        mode="arrow_keys",
        direction=True,
        **kwargs,
    ):
        px_to_adjust_by = max(px_to_adjust_by, 10)
        # Stamp the initial time before reading began
        read_mode_time_used = time.time()
        mode = "wheel"
        if mode == "arrow_keys":
            key = K_Keys["ArrowDown"]
            if not direction:
                key = K_Keys["ArrowUp"]
            self.read_with_arrow_keys(html_web_element, px_to_adjust_by, key, direction)
            # Wait to complete scroll
            asyncio.sleep(0.12)
        elif mode == "wheel":
            if random.random() < 0.65:
                element_screen_position = (
                    self.get_element_window_location_screen_offsets(html_web_element)
                )
                self.move_mouse_to_random_area_on_screen(
                    {
                        "x": element_screen_position["html_web_element"][0],
                        "y": self.get_document_offset_from_screen()["y"],
                        "width": html_web_element.rect["width"],
                        "height": min(
                            element_screen_position["html_web_element"][2],
                            self.get_browser_inner_size()["height"],
                        ),
                    }
                )
            if random.random() < 0.22:
                self.mouse.mouse_wheel_with_bezier_animation(
                    *pyautogui.position(), px_to_adjust_by, direction
                )
            else:
                self.mouse.mouse_wheel(
                    *pyautogui.position(),
                    px_to_adjust_by,
                    deltaY=self.identity.mouse_delta_y,
                    vary_deltaY_on_read=True,
                    yDirection=direction,
                )
        elif mode == "touch":
            if not direction:
                px_to_adjust_by *= -1
            self.read_with_touch(px_to_adjust_by)
        elif mode == "mouse_to_scrollbar":

            async def read_with_mouse_to_scrollbar():
                browser_inner_size_height = self.get_browser_inner_size()["height"]
                mouse_x, mouse_y = pyautogui.position()
                mouse_x += global_utils.fetch_percentage_value(
                    browser_inner_size_height, random.randint(0, 1)
                )
                px_to_adjust_mouse_y_by = max(
                    (
                        (
                            px_to_adjust_by
                            / self.web_browser_driver.execute_script(
                                "return document.body.getBoundingClientRect().height"
                            )
                        )
                        * browser_inner_size_height
                    ),
                    3,
                )
                if not direction:
                    px_to_adjust_mouse_y_by *= -1
                mouse_y += px_to_adjust_mouse_y_by
                print("mouse_y ==>", mouse_y)
                kwargs["present_mouse_points"]["x"] = mouse_x
                kwargs["present_mouse_points"]["y"] = mouse_y
                self.read_with_mouse_to_scrollbar(
                    {
                        "x": mouse_x,
                        "y": mouse_y,
                        "x_offset_percentage": 0,
                        "y_offset_percentage": 0,
                        "max_overshoot": 0,
                        "probability_of_overshoot": 0,
                    }
                )

            if "present_mouse_points" in kwargs:
                read_with_mouse_to_scrollbar()
            else:
                present_mouse_points = self.send_mouse_to_scrollbar()
                if not isinstance(present_mouse_points, dict):
                    raise TypeError(
                        "Set Function Asynchronous Parameter To False, If Expecting Dict Of Mouse Coordinates"
                    )
                kwargs["present_mouse_points"] = present_mouse_points
                asyncio.sleep(random.uniform(0, 1))
                read_with_mouse_to_scrollbar()
        kwargs["read_mode_time_used"] = time.time() - read_mode_time_used
        return kwargs

    async def smart_human_like_content_navigator(
        self,
        read_time,
        html_web_element,
        total_px_to_adjust_by,
        mode="arrow_keys",
        **kwargs,
    ):
        # This is to make up for the edge case, in the event there is no reason to simulate a read
        if total_px_to_adjust_by <= 0:
            asyncio.sleep(read_time)
            return True
        # Stamping the initial time before content will be read or adjusted by with px_to_adjust_by
        read_mode_initial_time_stamp = time.time()

        if await self.smart_ad_click():
            return "ad_clicked"

        element_coordinates = await self.get_element_location_window_offset(
            html_web_element
        )
        browser_inner_size = await self.get_browser_inner_size()

        element_base_offset = element_coordinates.get("y_offset")

        # The number of seconds to spend on each px
        avg_time_per_px = read_time / total_px_to_adjust_by

        px_adjusted_by = kwargs.get("px_adjusted_by", 0)
        if px_adjusted_by > total_px_to_adjust_by:
            px_adjusted_by = total_px_to_adjust_by
        read_mode_time_used = kwargs.get("read_mode_time_used", 0)
        time_allocated_to_px_adjusted_by = min(
            avg_time_per_px * px_adjusted_by, read_time
        )
        time_allocated_time_used_margin = (
            time_allocated_to_px_adjusted_by - read_mode_time_used
        )

        # print("px adjusted by ===>", px_adjusted_by)
        # print("total px to adjust by ===>", total_px_to_adjust_by)
        # print("read time ===>", read_time)
        # print("time expected to have used based on px adjusted ==>", time_allocated_to_px_adjusted_by)
        # print("time expected time used margin ==>", time_allocated_time_used_margin)

        time_to_pause_activity = 0
        # if the margin between time allocated and time used to read is lesser than 0, do not wait and amplify
        # px_to_adjust_by
        if time_allocated_time_used_margin <= 0:
            # Unlike calculation used for px_to_adjust_by below,amplify by setting destination to the lower ends of page
            px_to_adjust_by = round(
                random.uniform(
                    browser_inner_size.get("height") / 1.4,
                    browser_inner_size.get("height"),
                )
            )

            # Makes sure px_to_adjust_by is never greater than rem_px_to_adjust_by or total_px_to_adjust_by to try and
            # put a lid on overshooting
            if (
                kwargs.get("rem_px_to_adjust_by", total_px_to_adjust_by)
                < px_to_adjust_by
            ):
                px_to_adjust_by = kwargs.get(
                    "rem_px_to_adjust_by", total_px_to_adjust_by
                )
        else:
            # Use Portion of The Browser Inner Size to Determine How Long to Adjust PX by, and if the remaining px to
            # adjust by is lesser than the browser inner size to use, use it so the navigation doesn't scroll the
            # element out of desired offset
            px_to_adjust_by = round(
                random.uniform(1, browser_inner_size.get("height") / 1.4)
            )

            # Makes sure px_to_adjust_by is never greater than rem_px_to_adjust_by or total_px_to_adjust_by to try and
            # put a lid on overshooting
            if (
                kwargs.get("rem_px_to_adjust_by", total_px_to_adjust_by)
                < px_to_adjust_by
            ):
                px_to_adjust_by = kwargs.get(
                    "rem_px_to_adjust_by", total_px_to_adjust_by
                )

            # This is the time activity will be suspended for as thou it's trying to human read the content
            time_to_pause_activity = time_allocated_time_used_margin

            # navigate up as thou looking for forgotten content, feature to reinforce human reading behaviour
            if random.random() < 0.2:
                # Humans might wait at very different durations before scrolling up to check for some content-text,
                # the sleep below attempts to simulate that by taking no more than a minimal amount which would
                # inevitably affect the read_mode_time_used
                time_to_randomly_wait_before_scrolling_up = random.uniform(
                    0.01, time_to_pause_activity * 0.17
                )
                asyncio.sleep(time_to_randomly_wait_before_scrolling_up)

                px_to_move_by = browser_inner_size.get("height") * random.uniform(
                    0.15, 0.35
                )

                kwargs["read_by_mode_data"] = self.read_by_mode(
                    html_web_element,
                    px_to_move_by,
                    mode,
                    False,
                    **kwargs.get("read_by_mode_data", {}),
                )

                # modifying time_to_pause_activity on how long to wait for after navigating up. expected mean time to
                # be around 45% which averagely should not be more than half of time_to_pause_activity
                time_to_pause_activity = await global_utils.fetch_percentage_value(
                    time_to_pause_activity,
                    random.uniform(35, 55)
                    - (
                        +(kwargs["read_by_mode_data"]["read_mode_time_used"])
                        + time_to_randomly_wait_before_scrolling_up / 2
                    ),
                )

                #    print("Time to pause activity one ==>", time_to_pause_activity)
                asyncio.sleep(max(0, time_to_pause_activity))

                # Attempt to return page to original point before going up
                kwargs["read_by_mode_data"] = self.read_by_mode(
                    html_web_element,
                    px_to_move_by,
                    mode,
                    True,
                    **kwargs.get("read_by_mode_data", {}),
                )

                # Recalibrate time_to_pause_activity and deduct time used navigating down
                time_to_pause_activity = time_allocated_time_used_margin - (
                    time_to_pause_activity
                    + kwargs["read_by_mode_data"]["read_mode_time_used"]
                    + time_to_randomly_wait_before_scrolling_up / 2
                )

                #    print("Time to pause activity two ==>", time_to_pause_activity)

                # Finally, sleep for the remaining time if remaining
                asyncio.sleep(max(0, time_to_pause_activity))
            else:
                asyncio.sleep(time_to_pause_activity)

        # Store read_by_mode data at each function iteration to be repassed, reason is for read_by_mode
        # mouse_to_scrollbar mode
        kwargs["read_by_mode_data"] = self.read_by_mode(
            html_web_element,
            px_to_adjust_by,
            mode,
            True,
            **kwargs.get("read_by_mode_data", {}),
        )

        # Recalculating read_mode_time_used to show time spent adjusting or navigating the content,
        # recur time_allocated_time_used_margin to it if in deficit, so it doesn't forget it's behind if so,
        # adding time_to_pause_activity to offset the time waited for and leave only read_mode_time_used
        kwargs["read_mode_time_used"] = (
            time.time() - read_mode_initial_time_stamp
        ) + time_to_pause_activity

        # print("read mode duration ==>", read_mode_time_used)

        element_coordinates = self.get_element_location_window_offset(html_web_element)
        # Changing The Value Of px_to_adjust_by To The Amount Of px Actually Adjusted
        kwargs["px_adjusted_by"] = element_base_offset - element_coordinates.get(
            "y_offset"
        )
        # Calculating Remaining Px, making sure that it's not lesser than 0 at any given point
        kwargs["rem_px_to_adjust_by"] = (
            kwargs.get("rem_px_to_adjust_by", total_px_to_adjust_by) - px_adjusted_by
        )

        # print("remaining px to adjust by ==>", kwargs["rem_px_to_adjust_by"])

        if kwargs["rem_px_to_adjust_by"] <= 0:
            return True

        if kwargs.get("px_adjusted_at_0_count", 0) > 1:
            return True

        if px_adjusted_by == 0:
            kwargs["px_adjusted_at_0_count"] = (
                kwargs.get("px_adjusted_at_0_count", 0) + 1
            )
        else:
            kwargs["px_adjusted_at_0_count"] = 0

        return self.smart_human_like_content_navigator(
            read_time, html_web_element, total_px_to_adjust_by, mode, **kwargs
        )

    async def calculate_and_generate_page_read_time(
        self,
        html_web_element_to_read: WebElement = None,
        reading_speed=700,
        offset=20,
    ):
        """
        A Method To Calculate And Generate an Expected Read Time For Web Text Content Based On Set 'Words Scanning Per
        Minute(WSPM)' With Randomly Generated Offsets At a Max Which Can Be Either Positive or Negative
        :param html_web_element_to_read: Element Containing Web Text Content To Read On. If None, Method Tries To
        Fetch The Article Element Of The Web Page
        :param reading_speed: The Set Reading Speed Of Which Calculations Will Be Performed Upon.
        :param max_offset: The Maximum Percentage A Randomly Generated Offset Can Attain Either Positive or Negative
        :return: Returns Amount Of Seconds To Read Content For
        """
        if not html_web_element_to_read:
            html_web_element_to_read = self.web_browser_driver.find_element(
                By.TAG_NAME, "article"
            )

        all_element_words = html_web_element_to_read.text.split()
        words_len = len(all_element_words)
        seconds_to_read = (words_len / reading_speed) * 60
        seconds_to_read += seconds_to_read * offset / 100

        # Convert To Seconds And Return
        return round(seconds_to_read)

    async def read_element_content(self, html_web_element: WebElement):
        """
        This Method Scrolls The Web Page To Put Requested Web Element In View
        :param html_web_element: HTML Web Element To Scroll To
        :return: Return True When Scroll Is Complete
        """
        time_started = time.time()
        # There is a potential that the browser inner size might not be fully deducted from the content height to read
        # from. Therefore, the remaining should be adjusted unto the rest
        px_owing = -self.get_browser_inner_size()["height"]

        async def read(
            read_time,
            html_web_element: WebElement,
            mode,
            percentage_of_content_to_read=100,
        ):
            """
            Send Information To Looper To Read Content By Set Amount Of Content And Time
            :param read_time: Amount Of Time To Move Through Content
            :param html_web_element: HTML Web Element To Scroll To
            :param mode: Mode Of Navigation To Use, Usable Values are (arrow_keys, touch, mouse_to_scrollbar,
            mouse_scroll)
            :param percentage_of_content_to_read: Percentage Of Article Height To Stop At
            :return: True
            """
            nonlocal px_owing
            # Get The Total Pixels To Move By Using The percentage_of_content_to_read On html_web_element Height
            total_px_to_adjust_by = (
                await global_utils.fetch_percentage_value(
                    await html_web_element.get_position().height,
                    percentage_of_content_to_read,
                )
                + px_owing
            )
            px_owing = min(0, total_px_to_adjust_by)
            return await self.smart_human_like_content_navigator(
                read_time, html_web_element, total_px_to_adjust_by, mode
            )

        seconds_to_read = self.calculate_and_generate_page_read_time(
            html_web_element, self.reading_speed, random.randint(-15, 12)
        )
        content_read_percentage = random.randint(85, 100)
        print(
            f"Bot Process Id {self.bot_process_id} <:::> Percentage Of Content To Read And Seconds To Read For: ",
            content_read_percentage,
            seconds_to_read,
        )
        self.scroll_element_into_vertical_view(html_web_element, element_scroll_to=0)
        px_owing += self.get_element_location_window_offset(html_web_element).get(
            "y_offset"
        )
        # This sleep is to simulate a pause at the beginning of the article
        asyncio.sleep(random.uniform(2.45, 5.24))
        remaining_reading_content_percentage = content_read_percentage
        browser_inner_size = self.get_browser_inner_size()

        mode = ""
        while (
            remaining_reading_content_percentage > 0
            and self.get_element_location_window_offset(html_web_element).get("bottom")
            > browser_inner_size.get("height")
        ):
            if remaining_reading_content_percentage < 50 and random.random() < 0.08:
                print(
                    f"Bot Process Id {self.bot_process_id} <:::> Current Activity --> Scrolling To random.m Point On "
                    f"Article"
                )
                random_max = 100 - remaining_reading_content_percentage
                self.scroll_to_percentage_in_element(
                    html_web_element,
                    random.uniform(1, random_max),
                    random.uniform(0.9, 2),
                )

            # Release Mouse Hold If Mode In Last Read Was Mouse To ScrollBar
            if mode == "mouse_to_scrollbar":
                pyautogui.mouseUp()
                SmartHumanReader.active_on_mouse_movement.value = (
                    -self.bot_process_id if self.bot_process_id != 0 else -500
                )

            mode = "arrow_keys"
            # use device type
            if self.has_touch:
                mode = "touch"
            elif self.has_mouse:
                if (
                    random.random() < bot_constants.USE_MOUSE_READ_PROBABILITY
                    and SmartHumanReader.active_on_mouse_movement.value < 0
                ):
                    mode = "wheel"
                    SmartHumanReader.active_on_mouse_movement.value = (
                        self.bot_process_id
                    )
                    # The scrollbar on mac os is not prominent, and also people seldom use it anymore these days.
                    if (
                        self.identity.os is not device_constants.MAC_OS
                    ) and random.random() <= 0.05:
                        mode = "mouse_to_scrollbar"
                    self.bring_window_to_front()

            if remaining_reading_content_percentage < 26:
                next_read_sequence_percentage = remaining_reading_content_percentage
                remaining_reading_content_percentage = 0
            else:
                next_read_sequence_percentage = random.randint(
                    25, remaining_reading_content_percentage
                )
                remaining_reading_content_percentage -= next_read_sequence_percentage

            next_read_sequence_time = global_utils.fetch_percentage_value(
                seconds_to_read,
                next_read_sequence_percentage + random.uniform(-1.2, 1.2),
            )

            # There are possibilities next_read_sequence_time could be less than zero, resetting
            if next_read_sequence_time < 0:
                next_read_sequence_time = 0

            print(
                f"Bot Process Id {self.bot_process_id} <:::> Navigation Mode -->", mode
            )
            print(
                f"Bot Process Id {self.bot_process_id} <:::> Remaining Content Percentage To Read -->",
                remaining_reading_content_percentage,
            )

            if (
                read(
                    next_read_sequence_time,
                    html_web_element,
                    mode,
                    next_read_sequence_percentage,
                )
                == "ad_clicked"
            ):
                print(
                    f"BOT PROCESS ID {self.bot_process_id} <:::> AD WAS CLICKED, STOPPED READING ARTICLE"
                )
                return "ad_clicked"
        if mode == "mouse_to_scrollbar":
            pyautogui.mouseUp()
            SmartHumanReader.active_on_mouse_movement.value = (
                -self.bot_process_id if self.bot_process_id != 0 else -500
            )
        print(
            f"ARTICLE READ SESSION COMPLETED, BOT THREAD ID {self.bot_process_id} | TIME SPENT: "
            f"{time.time() - time_started}"
        )
        return True
