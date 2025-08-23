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


class PumpFunSelenium(BaseSelenium):

    def __init__(self):
        super().__init__()

        self.name = 'test'

        # Only request URLs containing "hoteles" or "whatever" will now be captured
        self.driver.scopes = [
            '.*pump.*',
        ]

        self.params = {}

    def get_rooms(self, params):
        logger.debug(f'get_rooms: {params}')
        self.params = params

        response = {}

        location = self.params.get('location')

        url = f'https://pump.fun/coin/{location}'
        self.driver.get(url)

        self.random_wait()

        bounding_curve_percentage = "/html/body/main/div[1]/div[2]/div[2]/div[2]/div[4]/div[1]/span"
        try:
            input_element_selection = self.wait.until(
                EC.presence_of_element_located((By.XPATH, bounding_curve_percentage)))
        except:
            print(f'Element not found or webpage not loaded in time: {bounding_curve_percentage}')
            self.save_screenshot()
            raise Exception(f'Element not found or webpage not loaded in time: {bounding_curve_percentage}')

        # print(f'Bounding curve for {location}: {input_element_selection.text}')
        response['bounding_curve_progress'] = input_element_selection.text

        self.save_screenshot()

        self.exit_driver()

        return response
