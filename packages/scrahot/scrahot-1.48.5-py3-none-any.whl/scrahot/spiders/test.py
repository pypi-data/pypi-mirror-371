import calendar
import datetime
import json
import os
import random
import time

from loguru import logger
from selenium.common import NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from seleniumwire.utils import decode

import scrahot
from scrahot.spiders.base import BaseSelenium


class TestSelenium(BaseSelenium):

    def __init__(self):
        super().__init__()

        self.name = 'test'

        # Only request URLs containing "hoteles" or "whatever" will now be captured
        # self.driver.scopes = [
        #     '.*hoteles.*',
        # ]

        self.params = {}

    def get_rooms(self, params):
        logger.debug(f'get_rooms: {params}')
        self.params = params

        response = {}

        website = self.params.get('website')
        location = self.params.get('location')

        start_date = datetime.datetime.strptime(self.params.get('date_range').get('start'), '%Y-%m-%d')
        start_day = start_date.day
        start_month = calendar.month_name[start_date.month]
        start_year = start_date.year

        end_date = datetime.datetime.strptime(self.params.get('date_range').get('end'), '%Y-%m-%d')
        end_day = end_date.day
        end_month = calendar.month_name[end_date.month]
        end_year = end_date.year

        adults = self.params.get('persons').get('adults')
        children = self.params.get('persons').get('children')
        adults = int(adults)
        children = int(children)

        # url = "http://host.docker.internal:8000/print-request-info" # f'https://{location}'
        url = f'https://{location}'
        self.driver.get(url)

        # Wait a bit
        time.sleep(20)

        # Look for any input in the page
        input_elements = self.driver.find_elements(By.TAG_NAME, "input")

        # If there are some, click on the one allowing to "Verify you are human"
        if input_elements is not None:
            for element in input_elements:
                if "Verify you are human" in element.get_dom_attribute('value'):
                    print("Found button!, let's click on it")
                    element.click()
                    break

        # Wait a bit until 'https://nowsecure.nl' is loaded
        # time.sleep(20)

        for i in range(adults):
            self.random_wait()

        self.save_screenshot()

        self.exit_driver()

        return response
