import logging


def setup_logger(name="ish_bot_logger", level=logging.DEBUG):
    # Create a custom logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # Create a formatter and set it for the handler
    formatter = logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s")
    console_handler.setFormatter(formatter)

    # Add the handler to the logger if it's not already added
    if not logger.hasHandlers():
        logger.addHandler(console_handler)

    return logger


logger = setup_logger()
