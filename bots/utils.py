from typing import Union
import re, math, os, numpy as np
import random


def return_fingerprintables_spoof_js_code(
    offset_color=None,
    offset_color_value: Union[int, float, tuple] = 0,
    audio_context_offset: float = 0.0,
    font_width_offset: int = 0,
    font_height_offset: int = 0,
    webgl_offsets: tuple = (0.234567654, 0.05),
    navigator_platform=None,
    webgl_params: tuple = (
        "Google Inc. (Intel)",
        15,
        12,
        14,
        14,
        13,
        4,
        4,
        4,
        4,
        3,
        3,
        3,
        3,
        6,
        11,
        12,
        12,
        "Intel(R) HD Graphics",
    ),
    browser_vendor="",
    hardware_specs={"hardware_concurrency": 8, "memory": 8},
    has_battery=False,
    referrer="",
):
    """
    :param offset_color: Color Of The Canvas Value To Spoof, Value Ranges are r, g, b, a. If Dict Type, Extract Value From
    :param offset_color_value: Value Of The Offset Color To Spoof By
    :param audio_context_offset: Value Of The Audio Context Editables To Spoof By
    :param font_width_offset: Number By Which To Offset The Width Of an Attempted Generated Font
    :param font_height_offset: Number By Which To Offset The Height Of an Attempted Generated Font
    :param webgl_offsets: A Tuple Containing The Index Of The JS Arrays Of Which To Offset.
    And The Value Of Which To Offset The Index Value By
    :param webgl_params: Tuple Containing Parameters To Overwrite The JS Webgl Standard Params
    :return: Returns Generated JS Code
    """
    # Should Range between -1 and 1 on rg and -1 and 2 on ba
    red, green, blue, alpha = (0, 0, 0, 0)
    if isinstance(offset_color_value, tuple):
        if len(offset_color_value) == 4:
            red, green, blue, alpha = offset_color_value
        else:
            raise ValueError(
                "Offset Color Value In a Tuple Form Must Be Exactly 4 In Length, In Order: (R, G, B, A)"
            )
    else:
        if offset_color == "r" or offset_color == "red":
            red = offset_color_value
        elif offset_color == "g" or offset_color == "green":
            green = offset_color_value
        elif offset_color == "b" or offset_color == "blue":
            blue = offset_color_value
        elif offset_color == "a" or offset_color == "alpha":
            alpha = offset_color_value

    # Web GL Variabes and Checks

    # offsets
    webgl_value_index_seed, webgl_value_offset = webgl_offsets

    # params, : Value Is Most Probable Value Or Values With Potential Similar Values
    # 37445 is UNMASKED_VENDOR_WEBGL
    # 3379 Ranges Between 14, 15 : 16384
    # 36347 Ranges Between 12, 13 : 4096
    # 34076 Ranges Between 14, 15 : 16384
    # 34024 Ranges Between 14, 15 : 16384
    # 3386 Ranges Between 13, 14, 15 : 32768
    # 3413 Ranges Between 1, 2, 3, 4 : 8
    # 3412 Ranges Between 1, 2, 3, 4 : 8
    # 3411 Ranges Between 1, 2, 3, 4 : 8
    # 3410 Ranges Between 1, 2, 3, 4 : 8
    # 34047 Ranges Between 1, 2, 3, 4 : 16
    # 34930 Ranges Between 1, 2, 3, 4 : 16
    # 34921 Ranges Between 1, 2, 3, 4 : 16
    # 35660 Ranges Between 1, 2, 3, 4 : 16
    # 35661 Ranges Between 4, 5, 6, 7, 8 : 32
    # 36349 Ranges Between 10, 11, 12, 13 : 1024
    # 33902 Ranges Between 10, 11, 12, 13 : 1
    # 33901 Ranges Between 10, 11, 12, 13 : 1024
    (
        webgl_param_37445,
        webgl_param_3379,
        webgl_param_36347,
        webgl_param_34076,
        webgl_param_34024,
        webgl_param_3386,
        webgl_param_3413,
        webgl_param_3412,
        webgl_param_3411,
        webgl_param_3410,
        webgl_param_34047,
        webgl_param_34930,
        webgl_param_34921,
        webgl_param_35660,
        webgl_param_35661,
        webgl_param_36349,
        webgl_param_33902,
        webgl_param_33901,
        webgl_param_37446,
    ) = webgl_params
    code = ()
    return code


def insert_text_into_string(
    m_string: str, string_to_add: str, keyword=None, where_to_insert=False
):
    """
    A function That Inserts A String Into A Text Where Specified Keyword Exists At Index
    :param m_string: The Main String To Work ON
    :param string_to_add: Text To Insert Into The Main String
    :param keyword: Word To Use As Anchor For Text Insertion. If None is Provided. It Appends To Text End
    :param where_to_insert: False - Insert Before Keyword, True - Insert After Keyword
    :return: Returns The Final String Worked On
    """
    if isinstance(keyword, str):
        keyword_index = m_string.find(keyword)
        if keyword_index != -1:
            if where_to_insert:
                keyword_index = keyword_index + len(keyword)
            new_string = (
                m_string[0:keyword_index] + string_to_add + m_string[keyword_index:-1]
            )
            return new_string
        pass
    if where_to_insert:
        new_string = m_string + string_to_add
    else:
        new_string = string_to_add + m_string
    return new_string


def insert_text_into_string_reg(
    m_string: str, string_to_add: str, regex=None, where_to_insert=False
):
    """
    A function That Inserts A String Into A Text Where Specified Keyword Exists At Index
    :param m_string: The Main String To Work ON
    :param string_to_add: Text To Insert Into The Main String
    :param regex: Regex To Use As Anchor For Text Insertion. If None is Provided. It Appends To Text End
    :param where_to_insert: False - Insert Before Keyword, True - Insert After Keyword
    :return: Returns The Final String Worked On
    """
    if isinstance(regex, str):
        keyword_index = re.search(regex, m_string).span()[1]
        if keyword_index:
            if not where_to_insert:
                keyword_index = re.search(regex, m_string).span()[0]
            new_string = (
                m_string[0:keyword_index] + string_to_add + m_string[keyword_index:-1]
            )
            return new_string
        pass
    if where_to_insert:
        new_string = m_string + string_to_add
    else:
        new_string = string_to_add + m_string
    return new_string


def fetch_percentage_value(number, percent):
    """
    A Simple Function To Calculate And Return The Value Of A Percentage On a Number
    :param number: The Number To Calculate On
    :param percent: The Percentage Of Number Needed
    :return: The Value Of The Percentage
    """
    value = number * percent / 100
    return value


def fetch_value_percentage(number, value):
    """
    A Simple Function Which In Reverse Fetches The Percent Of A Value To a Number
    :param number: Main Number Value
    :param value: Value Through Which To Fetch The Percentage On The Number
    :return: The Percentage Of The Value
    """
    percentage = value * 100 / number
    return percentage


def clean_negative(value):
    if isinstance(value, tuple):
        new_value = []
        for val in value:
            new_value.append(clean_negative(val))
        return tuple(new_value)
    elif value < 0:
        return value * -1
    return value


def find_points_distance_on_2d_cartesian_plane(point_1: tuple, point_2: tuple):

    x1, y1 = point_1
    x2, y2 = point_2

    xs_margin = math.pow(x2 - x1, 2)
    ys_margin = math.pow(y2 - y1, 2)

    return math.sqrt(clean_negative(xs_margin) + clean_negative(ys_margin))


def calculate_list_sum(values: list):
    values_sum = 0
    for value in values:
        if isinstance(value, list):
            calculate_list_sum(value)
        else:
            values_sum += value
    return values_sum


def generate_uniform_numbers_to_specific_range_and_sum(
    value_range: tuple = (0, 1), total_values_length=10, sum=5
):
    if value_range[0] < 0 or value_range[0] >= value_range[1]:
        raise ValueError(
            "Minimum Range Cannot Be Lesser Than Zero(0) or Greater Than, Equal To Maximum Range"
        )
    elif value_range[1] > sum:
        value_range = (value_range[0], sum)
    elif value_range[1] < (sum / total_values_length):
        print(
            f"Maximum Range Of {value_range[1]} Has Been Overwritten With {sum / total_values_length}, \
                      Because You Attempted To Create A Scenario Where The Sum Of The Maximum Range Given Can't Be, \
                      Equal To The Desired Sum And Length"
        )
        value_range = (value_range[0], sum / total_values_length)

    def scale_list_values(values: list, value_range: tuple, scaler):
        overhead = 0
        for i in range(len(values)):
            value = values[i] + scaler
            if not (value < value_range[0] or value > value_range[1]):
                values[i] = value
            else:
                overhead += scaler
        return overhead

    values = []
    values_sum = 0
    for i in range(total_values_length):
        values.append(random.uniform(*value_range))
        values_sum += values[i]
    offset_from_expected_sum = sum - values_sum
    # Loop Should Not Exceed Count
    count = 3
    overhead = scale_list_values(
        values, value_range, offset_from_expected_sum / total_values_length
    )
    while count >= 0 and overhead != 0:
        overhead = scale_list_values(
            values, value_range, overhead / total_values_length
        )
        count -= 1

    if overhead != 0:
        print("Unable To Generate Accurate Sum With Given Parameters")

    values_sum = calculate_list_sum(values)
    return values, values_sum, overhead == 0


def calculate_needed_points_from_coords_distance(
    distance, average_synaptic_latency, duration
):
    average_synaptic_latency *= 1000
    duration *= 1000
    pixels_per_dispatched_event = distance * average_synaptic_latency / duration
    needed_points = distance / pixels_per_dispatched_event
    if needed_points > distance:
        return distance
    return needed_points


def fetch_random_file_name_from_directory(
    directory: str, value_to_look_in_filename=None, recurse_mode=True
):
    directory_files = os.listdir(directory)

    if value_to_look_in_filename and not recurse_mode:
        for i in range(len(directory_files)):
            if not directory_files[i].find(value_to_look_in_filename):
                directory_files.pop(i)
    selected_filename = directory_files[random.randint(0, len(directory_files) - 1)]
    if recurse_mode and value_to_look_in_filename:
        if not selected_filename.find(value_to_look_in_filename):
            fetch_random_file_name_from_directory(
                directory, value_to_look_in_filename, recurse_mode
            )

    return selected_filename


def fetch_random_window_size_relative_to_screen(screen_width, screen_height):
    dimensions_to_use = (
        int(screen_width - fetch_percentage_value(screen_width, random.uniform(6, 30))),
        int(
            screen_height - fetch_percentage_value(screen_height, random.uniform(6, 30))
        ),
    )
    return dimensions_to_use


def url_ends_with(string, endings):
    for ending in endings:
        if (
            string.endswith(ending)
            or (ending + "?" in string)
            or (ending + "%3F" in string)
        ):
            return True
    return False


def has_string_in(string_to_test, strings_against):
    for string_against in strings_against:
        if string_against in string_to_test:
            return True
    return False


def normalize_to_target(arr, target):
    if not arr:
        return []

    total = sum(arr)
    if total == 0:
        raise ValueError("Sum of the array elements is zero, cannot normalize.")

    # Calculate normalized values with floating point precision
    normalized = [x * target / total for x in arr]

    # Calculate the difference due to rounding and distribute it
    rounded = [int(round(x)) for x in normalized]
    difference = target - sum(rounded)

    if difference == 0:
        return rounded

    # Adjust the rounding to account for the difference
    # Distribute the difference by adjusting the elements with the largest errors first
    errors = [(normalized[i] - rounded[i], i) for i in range(len(arr))]
    errors.sort(reverse=True)

    for i in range(abs(difference)):
        index = errors[i % len(errors)][1]
        if difference > 0:
            rounded[index] += 1
        else:
            rounded[index] -= 1

    return rounded


def cubic_bezier(t, p0, p1, p2, p3):
    return (
        (1 - t) ** 3 * p0
        + 3 * (1 - t) ** 2 * t * p1
        + 3 * (1 - t) * t**2 * p2
        + t**3 * p3
    )


def plot_cubic_bezier(p0, p1, p2, p3, num_points=100):
    t_values = np.linspace(0, 1, num_points)
    values = []
    for t in t_values:
        x, y = cubic_bezier(t, p0, p1, p2, p3)
        values.append([x, y])

    return values


def generate_mouse_wheel_plot(px_to_adjust_by=1000, duration=3000):
    p0 = np.array([0, 0])
    p1 = np.array([0.3, 1])
    p2 = np.array([0.5, 0])
    p3 = np.array([1, 0])

    plots = plot_cubic_bezier(p0, p1, p2, p3, round(px_to_adjust_by / 20))

    px_to_adjust = []
    duration_to_wait = []
    for plot in plots:
        px_to_adjust.append(plot[1])
        duration_to_wait.append(plot[0])
    try:
        px_to_adjust = normalize_to_target(px_to_adjust, px_to_adjust_by)
        duration_to_wait = normalize_to_target(duration_to_wait, duration)
    except ValueError:
        return []
    return [
        (
            [duration_to_wait[i], px_to_adjust[i]]
            if px_to_adjust[i] >= 1
            else [duration_to_wait[i], 1]
        )
        for i in range(len(duration_to_wait))
    ]


def normalize_version(version, indexes=4):
    parts = str(version).split(".")[:indexes]
    return ".".join(parts + ["0"] * (indexes - len(parts)))


import os


def remove_profile_lock(profile_path):
    lock_files = ["SingletonLock"]
    for lock_file in lock_files:
        lock_path = os.path.join(profile_path, lock_file)
        if os.path.exists(lock_path) or os.path.islink(lock_path):
            try:
                os.remove(lock_path)
                print(f"Removed lock file: {lock_path}")
            except Exception as e:
                print(f"Error removing lock file {lock_path}: {e}")
