import pyautogui
import random
import time
import asyncio
from typing import TypedDict, Dict, List

from nodriver import Element as WebElement

from bots import utils as global_utils
from constants import bot_constants, device_constants
from constants.keyboard_keys import Keys as K_Keys
from humanbehaviourmechanics.human_behaviour_reveries import HumanBehaviourReveries
from humanbehaviourmechanics.human_movements import HumanMovements
from humanbehaviourmechanics.smart_ads_interactions import SmartAdsInteractions
from log import logger


class SmartHumanReader(HumanMovements, SmartAdsInteractions, HumanBehaviourReveries):
    def __init__(self, reading_speed=900, no_of_clicks=0):
        self.reading_speed = reading_speed
        HumanMovements.__init__(self, no_of_clicks)
        SmartAdsInteractions.__init__(self, no_of_clicks)
        HumanBehaviourReveries.__init__(self)

    async def read_by_mode(
        self,
        html_web_element: WebElement,
        px_to_adjust_by,
        mode="arrow_keys",
        direction=True,
    ):
        px_to_adjust_by = max(px_to_adjust_by, 10)
        if random.random() < 0.5 and not self.identity.has_touch:
            logger.info("<--> Moving To Random Area On Reading Element <-->")
            await self.move_mouse_to_random_area_on_element(html_web_element)
            await self.smart_click_trigger(probability=1)
        if mode == "arrow_keys":
            await self.read_with_arrow_keys(px_to_adjust_by, direction)
            # Wait to complete scroll
            await asyncio.sleep(0.12)
        elif mode == "wheel":
            if random.random() < 0.68:
                await self.mouse.mouse_wheel_with_bezier_animation(
                    *pyautogui.position(), px_to_adjust_by, direction
                )
            else:
                await self.mouse.mouse_wheel(
                    *pyautogui.position(),
                    px_to_adjust_by,
                    deltaY=self.identity.mouse_delta_y,
                    vary_deltaY_on_read=True,
                    yDirection=direction,
                )
        elif mode == "touch":
            if not direction:
                px_to_adjust_by *= -1
            await self.read_with_touch(px_to_adjust_by)

    async def smart_human_like_content_navigator(
        self,
        read_time,
        html_web_element: WebElement,
        total_px_to_adjust_by,
        mode="arrow_keys",
        **kwargs,
    ):
        # This is to make up for the edge case, in the event there is no reason to simulate a read
        if total_px_to_adjust_by <= 0:
            await asyncio.sleep(read_time)
            return True
        # Stamping the initial time before content will be read or adjusted by with px_to_adjust_by
        read_mode_initial_time_stamp = time.time()

        if await self.smart_ad_click():
            return "ad_clicked"

        browser_inner_size = await self.get_browser_inner_size()

        element_base_offset = (await html_web_element.get_position()).y

        # The number of seconds to spend on each px
        avg_time_per_px = read_time / total_px_to_adjust_by

        time_owed = kwargs.get("time_owed", 0)

        px_to_adjust_by = round(
            random.uniform(
                browser_inner_size.get("height") / 1.4,
                browser_inner_size.get("height"),
            )
        )
        if kwargs.get("rem_px_to_adjust_by", total_px_to_adjust_by) < px_to_adjust_by:
            px_to_adjust_by = kwargs.get("rem_px_to_adjust_by", total_px_to_adjust_by)

        time_to_pause_activity = px_to_adjust_by * avg_time_per_px

        # navigate up as thou looking for forgotten content, feature to reinforce human reading behaviour
        if time_owed > 0:
            time_to_pause_activity = 0
        else:
            if random.random() < 0.2:
                await asyncio.sleep(random.uniform(0.4, 1.4))

                await self.read_by_mode(
                    html_web_element,
                    browser_inner_size.get("height") * random.uniform(0.15, 0.35),
                    mode,
                    False,
                )

                await asyncio.sleep(random.uniform(0.5, 2.5))

                # Attempt to return page to original point before going up
                await self.read_by_mode(
                    html_web_element,
                    browser_inner_size.get("height") * random.uniform(0.15, 0.35),
                    mode,
                    True,
                )

        await asyncio.sleep(time_to_pause_activity)

        await self.read_by_mode(
            html_web_element,
            px_to_adjust_by,
            mode,
            True,
        )

        # Changing The Value Of px_to_adjust_by To The Amount Of px Actually Adjusted
        kwargs["px_adjusted_by"] = (
            element_base_offset - (await html_web_element.get_position()).y
        )

        kwargs["time_owed"] = (
            time_owed
            + (time.time() - read_mode_initial_time_stamp)
            - (kwargs["px_adjusted_by"] * avg_time_per_px)
        )

        kwargs["rem_px_to_adjust_by"] = (
            kwargs.get("rem_px_to_adjust_by", total_px_to_adjust_by)
            - kwargs["px_adjusted_by"]
        )

        # if px_to_adjust_by is greater than px_adjusted_by by a margin of 100(acceptable margin) it means it couldn't go further because it's now at document end
        # Allowed for a wider margin because of touchscreen
        no_px_adjustment_threshold = 100
        if mode == "touch":
            no_px_adjustment_threshold = 400
        if kwargs["rem_px_to_adjust_by"] <= 0 or (
            (px_to_adjust_by - kwargs["px_adjusted_by"]) >= no_px_adjustment_threshold
        ):
            return True

        return await self.smart_human_like_content_navigator(
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
            html_web_element_to_read = self.active_tab.select("article")

        all_element_words = html_web_element_to_read.text_all.split()
        words_len = len(all_element_words)
        seconds_to_read = (words_len / reading_speed) * 60
        seconds_to_read += seconds_to_read * offset / 100

        # Convert To Seconds And Return
        return round(seconds_to_read)

    async def read_element_content(self, html_web_element: WebElement):
        """
        Intelligently reads an Element, Flunctuating heights on the elements could cause instability
        :param html_web_element: HTML Web Element To Scroll To
        :return: Return True When Scroll Is Complete
        """
        time_started = time.time()

        logger.info("<--> Calculating Seconds And Percentage To Read For <-->")
        seconds_to_read = await self.calculate_and_generate_page_read_time(
            html_web_element, self.reading_speed, random.randint(-15, 12)
        )
        content_read_percentage = random.randint(85, 100)
        logger.info(
            f"<--> Percentage Of Content To Read And Seconds To Read For:{content_read_percentage},{seconds_to_read} <-->"
        )
        logger.info("<--> Scrolling Element Into View <-->")
        await self.scroll_element_into_vertical_view(
            html_web_element, element_scroll_to=0
        )
        (await self.get_element_location_window_offset(html_web_element)).get(
            "y_offset"
        )
        # This sleep is to simulate a pause at the beginning of the article
        await asyncio.sleep(random.uniform(2.45, 5.24))
        remaining_reading_content_percentage = content_read_percentage
        browser_inner_size = await self.get_browser_inner_size()
        mode = ""
        while remaining_reading_content_percentage > 0 and (
            await html_web_element.get_position()
        ).bottom > browser_inner_size.get("height"):
            if remaining_reading_content_percentage < 50 and random.random() < 0.08:
                print(f"<--> Scrolling To Random Point On Article <-->")
                random_max = 100 - remaining_reading_content_percentage
                await self.scroll_to_percentage_in_element(
                    html_web_element,
                    random.uniform(1, random_max),
                    random.uniform(0.9, 10),
                )

            # Release Mouse Hold If Mode In Last Read Was Mouse To ScrollBar
            if mode == "mouse_to_scrollbar":
                pyautogui.mouseUp()
                SmartHumanReader.active_on_mouse_movement.value = (
                    -self.bot_process_id if self.bot_process_id != 0 else -500
                )
            mode = "arrow_keys"
            # use device type
            if self.identity.has_touch:
                mode = "touch"
            elif self.identity.has_mouse:
                if (
                    random.random() < bot_constants.USE_MOUSE_READ_PROBABILITY
                    and SmartHumanReader.active_on_mouse_movement.value < 0
                ):
                    mode = "wheel"
                    SmartHumanReader.active_on_mouse_movement.value = (
                        self.bot_process_id
                    )
                    asyncio.create_task(self.bring_window_to_front())

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

            # Get The Total Pixels To Move By Using The percentage_of_content_to_read On html_web_element Height
            total_px_to_adjust_by = global_utils.fetch_percentage_value(
                (await html_web_element.get_position()).height,
                next_read_sequence_percentage,
            )
            if (
                await self.smart_human_like_content_navigator(
                    next_read_sequence_time,
                    html_web_element,
                    total_px_to_adjust_by,
                    mode,
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


class Interactables(TypedDict):
    def __init__(
        self,
        buttons: List[WebElement],
        links: List[WebElement],
        inputs: List[WebElement],
        textareas: List[WebElement],
    ):
        self.buttons = buttons
        self.links = links
        self.inputs = inputs
        self.textareas = textareas

    async def to_dict(self) -> Dict[str, List[WebElement]]:
        return {
            "buttons": [self.buttons],
            "links": [self.links],
            "inputs": [self.inputs],
            "textareas": [self.textareas],
        }


class SmartHumanElementInteract(SmartHumanReader):
    def __init__(reading_speed=900, no_of_clicks=0):
        super().__init__(reading_speed, no_of_clicks)

    async def find_interactables(self, html_web_element: WebElement) -> Interactables:
        interactables: Interactables = {
            "buttons": await html_web_element.query_selector_all("button"),
            "links": await html_web_element.query_selector_all("a"),
            "inputs": await html_web_element.query_selector_all("input"),
            "textareas": await html_web_element.query_selector_all("textarea"),
        }
        return interactables

    async def type_input(self, input_webelement: WebElement, text: str) -> bool:
        self.click_on_element(input_webelement)
        return True

    async def interact_with_element_content(self, html_web_element: WebElement):
        await self.read_element_content(html_web_element)
