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
    referer="",
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
    code = (
        'var hardwareSpecsInject = function() {\n\
            Object.defineProperty(Navigator.prototype, "deviceMemory", {\n \
                "value":'
        + str(hardware_specs["memory"])
        + ' \n \
            }); \n \
            if("'
        + referer
        + '"){\n \
                Object.defineProperty(Document.prototype, "referrer", {\n \
                    "value":"'
        + str(referer)
        + '"\n \
                });\n \
            }\n \
        }\n \
        var browserSpecsInject = function() {\n\
            if ("'
        + browser_vendor
        + '") {\n \
                Object.defineProperty(Navigator.prototype, "vendor", {\n \
                    "value": "'
        + browser_vendor
        + '"\n \
                }); \n\
            }\n\
        }\n \
        var font_inject = function() {\n\
            var rand = {\n\
                "noise": function() {\n\
                    var SIGN = Math.random() < Math.random() ? -1 : 1;\n\
                    console.log(Math.floor(Math.random() + SIGN * Math.random()))\n\
                    return Math.floor(Math.random() + SIGN * Math.random());\n\
                },\n\
                "sign": function() {\n\
                    const tmp = [-1, -1, -1, -1, -1, -1, +1, -1, -1, -1];\n\
                    const index = Math.floor(Math.random() * tmp.length);\n\
                    return tmp[index];\n\
                }\n\
            };\n\
            Object.defineProperty(HTMLElement.prototype, "offsetHeight", {\n\
                get() {\n\
                    const height = Math.floor(this.getBoundingClientRect().height);\n\
                    const valid = height && rand.sign() === 1;\n\
                    const result = height + '
        + str(font_height_offset)
        + ';\n\
                    return result;\n\
                }\n\
            });\n\
            Object.defineProperty(HTMLElement.prototype, "offsetWidth", {\n\
                get() {\n\
                    const width = Math.floor(this.getBoundingClientRect().width);\n\
                    const valid = width && rand.sign() === 1;\n\
                    const result = width + '
        + str(font_width_offset)
        + ';\n\
                    return result;\n\
                }\n\
            });\n\
        };\n\
        var webgl_inject = function() {\n\
            var config = {\n\
                "random": {\n\
                    "value": function() {\n\
                        return Math.random();\n\
                    },\n\
                    "item": function(e) {\n\
                        var rand = e.length * config.random.value();\n\
                        return e[Math.floor(rand)];\n\
                    },\n\
                    "number": function(power) {\n\
                        if(power.isArray()) {\n\
                            var tmp = [];\n\
                            for (var i = 0; i < power.length; i++) {\n\
                                tmp.push(Math.pow(2, power[i]));\n\
                            }\n\
                            return Math.pow(2, power);\n\
                        }\n\
                        return config.random.item(tmp);\n\
                    },\n\
                    "int": function(power) {\n\
                        if(power.isArray()) {\n\
                            var tmp = [];\n\
                            for (var i = 0; i < power.length; i++) {\n\
                                var n = Math.pow(2, power[i]);\n\
                                tmp.push(new Int32Array([n, n]));\n\
                            }\n\
                            return config.random.item(tmp);\n\
                        }\n\
                        var n = Math.pow(2, power);\n\
                        return new Int32Array([n, n]);\n\
                    },\n\
                    "float": function(power) {\n\
                        if(power.isArray()) {\n\
                            var tmp = [];\n\
                            for (var i = 0; i < power.length; i++) {\n\
                                var n = Math.pow(2, power);\n\
                                tmp.push(new Float32Array([1, n]));\n\
                            }\n\
                            return config.random.item(tmp);\n\
                        }\n\
                        var n = Math.pow(2, power);\n\
                        return new Float32Array([1, n]);\n\
                    }\n\
                },\n\
                "spoof": {\n\
                    "webgl": {\n\
                        "buffer": function(target) {\n\
                            var proto = target.prototype ? target.prototype : target.__proto__;\n\
                            const bufferData = proto.bufferData;\n\
                            Object.defineProperty(proto, "bufferData", {\n\
                                "value": function() {\n\
                                    if (Math.min(...arguments[1]) >= 0 && arguments[1].constructor == Float32Array) {\n\
                                        var index = Math.floor('
        + str(webgl_value_index_seed)
        + " * arguments[1].length);\n\
                                        var noise = 0.1 * "
        + str(webgl_value_offset)
        + ';\n\
                                        arguments[1][index] = arguments[1][index] <= 0.5 ? arguments[1][index] + noise : arguments[1][index] - noise;\n\
                                    }\n\
                                    return bufferData.apply(this, arguments);\n\
                                }\n\
                            });\n\
                        },\n\
                        "parameter": function(target) {\n\
                            var proto = target.prototype ? target.prototype : target.__proto__;\n\
                            const getParameter = proto.getParameter;\n\
                            Object.defineProperty(proto, "getParameter", {\n\
                                "value": function() {\n\
                                    if (arguments[0] === 3415) return 0;\n\
                                    //else if (arguments[0] === 3414) return 24;\n\
                                    //else if (arguments[0] === 36348) return 30;\n\
                                    //else if (arguments[0] === 7936) return "WebKit";\n\
                                    else if (arguments[0] === 37445) return "'
        + str(webgl_param_37445)
        + '";\n\
                                    //else if (arguments[0] === 7937) return "WebKit WebGL";\n\
                                    //else if (arguments[0] === 3379) return config.random.number('
        + str(webgl_param_3379)
        + ");\n\
                                    //else if (arguments[0] === 36347) return config.random.number("
        + str(webgl_param_36347)
        + ");\n\
                                    //else if (arguments[0] === 34076) return config.random.number("
        + str(webgl_param_34076)
        + ");\n\
                                    //else if (arguments[0] === 34024) return config.random.number("
        + str(webgl_param_34024)
        + ");\n\
                                    //else if (arguments[0] === 3386) return config.random.int("
        + str(webgl_param_3386)
        + ");\n\
                                    //else if (arguments[0] === 3413) return config.random.number("
        + str(webgl_param_3413)
        + ");\n\
                                    //else if (arguments[0] === 3412) return config.random.number("
        + str(webgl_param_3412)
        + ");\n\
                                    //else if (arguments[0] === 3411) return config.random.number("
        + str(webgl_param_3411)
        + ");\n\
                                    //else if (arguments[0] === 3410) return config.random.number("
        + str(webgl_param_3410)
        + ");\n\
                                    //else if (arguments[0] === 34047) return config.random.number("
        + str(webgl_param_34047)
        + ");\n\
                                    //else if (arguments[0] === 34930) return config.random.number("
        + str(webgl_param_34930)
        + ");\n\
                                    //else if (arguments[0] === 34921) return config.random.number("
        + str(webgl_param_34921)
        + ");\n\
                                    //else if (arguments[0] === 35660) return config.random.number("
        + str(webgl_param_35660)
        + ");\n\
                                    //else if (arguments[0] === 35661) return config.random.number("
        + str(webgl_param_35661)
        + ");\n\
                                    //else if (arguments[0] === 36349) return config.random.number("
        + str(webgl_param_36349)
        + ");\n\
                                    //else if (arguments[0] === 33902) return config.random.float("
        + str(webgl_param_33902)
        + ");\n\
                                    //else if (arguments[0] === 33901) return config.random.float("
        + str(webgl_param_33901)
        + ');\n\
                                    else if (arguments[0] === 37446) return /*config.random.item(*/"'
        + str(webgl_param_37446)
        + '"/*)*/;\n\
                                    //else if (arguments[0] === 7938) return config.random.item(["WebGL 1.0", "WebGL 1.0 (OpenGL)", "WebGL 1.0 (OpenGL Chromium)"]);\n\
                                    //else if (arguments[0] === 35724) return config.random.item(["WebGL", "WebGL GLSL", "WebGL GLSL ES", "WebGL GLSL ES (OpenGL Chromium"]);*/\n\
                                    return getParameter.apply(this, arguments);\n\
                                }\n\
                            });\n\
                        }\n\
                    }\n\
                }\n\
            };\n\
            config.spoof.webgl.buffer(WebGLRenderingContext);\n\
            config.spoof.webgl.buffer(WebGL2RenderingContext);\n\
            config.spoof.webgl.parameter(WebGLRenderingContext);\n\
            config.spoof.webgl.parameter(WebGL2RenderingContext);\n\
            document.documentElement.dataset.wgscriptallow = true;\n\
        }; \n\
        var audiocontext_inject = function() {\n\
            const context = {\n\
                "BUFFER": null,\n\
                "getChannelData": function(e) {\n\
                    const getChannelData = e.prototype.getChannelData;\n\
                    Object.defineProperty(e.prototype, "getChannelData", {\n\
                        "value": function() {\n\
                            const results_1 = getChannelData.apply(this, arguments);\n\
                            if (context.BUFFER !== results_1) {\n\
                              context.BUFFER = results_1;\n\
                                for (var i = 0; i < results_1.length; i += 100) {\n\
                                    let index = Math.floor('
        + str(audio_context_offset)
        + " * i);\n\
                                    results_1[index] = results_1[index] + "
        + str(audio_context_offset)
        + ' * 0.0000001;\n\
                                }\n\
                            }\n\
                            return results_1;\n\
                        }\n\
                    });\n\
                },\n\
                "createAnalyser": function(e) {\n\
                    const createAnalyser = e.prototype.__proto__.createAnalyser;\n\
                    Object.defineProperty(e.prototype.__proto__, "createAnalyser", {\n\
                        "value": function() {\n\
                            const results_2 = createAnalyser.apply(this, arguments);\n\
                            const getFloatFrequencyData = results_2.__proto__.getFloatFrequencyData;\n\
                            Object.defineProperty(results_2.__proto__, "getFloatFrequencyData", {\n\
                                "value": function() {\n\
                                    const results_3 = getFloatFrequencyData.apply(this, arguments);\n\
                                    for (var i = 0; i < arguments[0].length; i += 100) {\n\
                                        let index = Math.floor('
        + str(audio_context_offset)
        + " * i);\n\
                                        arguments[0][index] = arguments[0][index] + "
        + str(audio_context_offset)
        + " * 0.1;\n\
                                    }\n\
                                    return results_3;\n\
                                }\n\
                            });\n\
                            return results_2;\n\
                        }\n\
                    });\n\
                }\n\
            };\n\
            context.getChannelData(AudioBuffer);\n\
            context.createAnalyser(AudioContext);\n\
            context.getChannelData(OfflineAudioContext);\n\
            context.createAnalyser(OfflineAudioContext);\n\
            document.documentElement.dataset.acxscriptallow = true;\n\
        };\n\
        \n\
        var canvas_inject = function() {\n\
            const toBlob = HTMLCanvasElement.prototype.toBlob;\n\
            const toDataURL = HTMLCanvasElement.prototype.toDataURL;\n\
            const getImageData = CanvasRenderingContext2D.prototype.getImageData;\n\
            var noisify = function(canvas, context) {\n\
                if (context) {\n\
                    const shift = {\n\
                        'r': Math.floor("
        + str(red)
        + "),\n\
                        'g': Math.floor("
        + str(green)
        + "),\n\
                        'b': Math.floor("
        + str(blue)
        + "),\n\
                        'a': Math.floor("
        + str(alpha)
        + ')\n\
                    };\n\
                    const width = canvas.width;\n\
                    const height = canvas.height;\n\
                    if (width && height) {\n\
                        const imageData = getImageData.apply(context, [0, 0, width, height]);\n\
                        for (let i = 0; i < height; i++) {\n\
                            for (let j = 0; j < width; j++) {\n\
                                const n = ((i * (width * 4)) + (j * 4));\n\
                                imageData.data[n + 0] = imageData.data[n + 0] == 0 || imageData.data[n + 0] == 255 ? imageData.data[n + 0] : imageData.data[n + 0] + shift.r;\n\
                                imageData.data[n + 1] = imageData.data[n + 1] == 0 || imageData.data[n + 1] == 255 ? imageData.data[n + 1] : imageData.data[n + 1] + shift.g;\n\
                                imageData.data[n + 2] = imageData.data[n + 2] == 0 || imageData.data[n + 2] == 255 ? imageData.data[n + 2] : imageData.data[n + 2] + shift.b;\n\
                                imageData.data[n + 3] = imageData.data[n + 3] == 0 || imageData.data[n + 3] == 255 ? imageData.data[n + 3] : imageData.data[n + 3] + shift.a;\n\
                            }\n\
                        }\n\
                        context.putImageData(imageData, 0, 0);\n\
                    }\n\
                }\n\
            };\n\
            Object.defineProperty(HTMLCanvasElement.prototype, "toBlob", {\n\
                "value": function() {\n\
                    noisify(this, this.getContext("2d"));\n\
                    return toBlob.apply(this, arguments);\n\
                }\n\
            });\n\
            Object.defineProperty(HTMLCanvasElement.prototype, "toDataURL", {\n\
                "value": function() {\n\
                    noisify(this, this.getContext("2d"));\n\
                    return toDataURL.apply(this, arguments);\n\
                }\n\
            });\n\
            Object.defineProperty(CanvasRenderingContext2D.prototype, "getImageData", {\n\
                "value": function() {\n\
                    noisify(this.canvas, this);\n\
                    return getImageData.apply(this, arguments);\n\
                }\n\
            });\n\
        document.documentElement.dataset.cbscriptallow = true;\n\
        };\n\
        var script_1 = document.createElement("script");\n\
        script_1.textContent = "(" + canvas_inject + ")();(" + audiocontext_inject + \
        ")();(" + webgl_inject + ")();(" + font_inject + ")();(" + hardwareSpecsInject + ")();(" + browserSpecsInject + ")();";\n\
        document.documentElement.appendChild(script_1);\n\
        window.top.document.documentElement.appendChild(script_1);\n\
        script_1.remove();\n \
'
    )
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
        screen_width - fetch_percentage_value(screen_width, random.uniform(6, 30)),
        screen_height - fetch_percentage_value(screen_height, random.uniform(6, 30)),
    )
    return dimensions_to_use


def url_ends_with(string, endings):
    for ending in endings:
        if string.endswith(ending) or (ending + "?" in string):
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

    px_to_adjust = normalize_to_target(px_to_adjust, px_to_adjust_by)
    duration_to_wait = normalize_to_target(duration_to_wait, duration)
    return [
        (
            [duration_to_wait[i], px_to_adjust[i]]
            if px_to_adjust[i] >= 1
            else [duration_to_wait[i], 1]
        )
        for i in range(len(duration_to_wait))
    ]
