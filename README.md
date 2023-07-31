# Web Page Human Behavior Simulation Bot

## Description
This Python script is a complex bot that simulates human behavior on a web page using Selenium WebDriver. The bot interacts with the web page, navigates through different elements, performs actions, and automates repetitive tasks, just like a human user would do. It is designed to be versatile and adaptable to various web pages and scenarios.

## Features
- Web page automation: The bot can interact with web pages using Selenium WebDriver, controlling browsers like Chrome, Firefox, etc.
- Navigating through pages: It can navigate through links, buttons, and other elements to access different parts of the web page.
- Form filling: The bot can fill out web forms with predefined or dynamic data, such as text inputs, dropdowns, radio buttons, checkboxes, etc.
- Clicking and scrolling: It can click on elements and scroll through the page to mimic human interaction.
- Waiting: The bot incorporates explicit and implicit waits to handle dynamic web pages and ensure synchronization with page loading.
- Randomized behavior: To simulate human-like activity, the bot includes randomization in its behavior, such as random delays between actions.
- Advanced human like mouse movement.

## Requirements
- Python >=3.9
- Selenium WebDriver
- Pyclick
- Chrome/Firefox WebDriver (depending on the browser used)

## Installation and Setup
1. Install Python >=3.9 from the official website: https://www.python.org/downloads/
2. Install Selenium WebDriver
3. Install Pyclick

4. Download the appropriate Chrome/Firefox WebDriver for your system and add it to your system's PATH.
- Chrome WebDriver: https://sites.google.com/a/chromium.org/chromedriver/downloads
- Firefox WebDriver: https://github.com/mozilla/geckodriver/releases

## Configuration
1. Open the `config.py` file and customize the following settings:
- `BROWSER`: Specify the browser you want to use (e.g., 'chrome' or 'firefox').
- `HEADLESS`: Set to `True` to run the browser in headless mode (without a visible GUI) or `False` to show the browser window.
- `WAIT_TIME`: Define the default wait time in seconds for explicit waits (to handle dynamic elements).
- Add any other configuration variables that suit your specific requirements.

## Usage
1. Place your web page URL in the `url` variable within the `run.py` script.
2. Customize the bot's behavior by modifying the functions and actions in `run.py`.
3. Run the bot using the following command when in the directory: `run.py`
