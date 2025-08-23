import calendar
import datetime
import json
import random
import re
import time
import traceback
import logging

from loguru import logger
# import pyautogui
from selenium.common import NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from seleniumwire.utils import decode

from scrahot.spiders.base import BaseSelenium
from scrahot.standard_json import get_standard_data_second
from scrahot.utils import XHRListener
import seleniumbase

class DecolarSeleniumBase(BaseSelenium):
    def __init__(self):
        super().__init__(driver_type='sb')

        self.name = 'decolar'

        self.params = {}

        self.requests_handle = XHRListener()

        # Configure SeleniumBase logging
        self._configure_sb_logging()

        # import platform
        # from importlib.metadata import version
        # from selenium import webdriver
        #
        # driver = webdriver.Chrome()
        #
        # print('Python Version'.ljust(25), platform.python_version())
        # print('Seleniumbase version'.ljust(25), version('seleniumbase'))
        # print('Chrome version'.ljust(25), driver.capabilities['browserVersion'])
        # print('Chromedriver Version'.ljust(25), driver.capabilities['chrome']['chromedriverVersion'].split(' ')[0])

    def wait_for_hermes_response(self, sb, timeout=30):
        """Wait for and capture the hermes-service response"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            # Check XHR responses for hermes-service
            loop = sb.cdp.get_event_loop()
            xhr_responses = loop.run_until_complete(self.requests_handle.receiveXHR(sb.cdp.page))

            for response in xhr_responses:
                if '/hermes-service/topic/accommodations_cluster_selection' in response["url"]:
                    logger.info(f"Found hermes-service response: {response['url']}")
                    return response

            sb.sleep(0.5)

        return None
    @logger.catch
    def get_rooms(self, params):
        logger.debug(f'get_rooms: {params}')
        self.params = params

        website, region, location, start_day, start_month, start_year, end_day, end_month, end_year, adults, children, start_date, end_date = self.validate_input_data()

        response = {
            "success": True,
            "search_criteria": params,
            "hotel": params.get('location'),
            "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
            'rooms': [],
        }
        current_url = None

        with (seleniumbase.SB(uc=True, test=True, locale_code="en", ad_block=True, window_size='1920,1080',
                            uc_cdp_events=True,  # Enable CDP Mode for advanced evasion
                            log_cdp_events={"performance": "ALL", "browser": "ALL"},

                            # driver_version=136,
                            headed=True,  # Use headful mode
                            xvfb=True,  # ← use the Xvfb server you just started (virtual display for Docker)
                            xvfb_metrics="1920,1080",
                            headless=False,  # ← disable Chrome’s built-in headless mode
                            headless1=False,
                            headless2=False,    # Use the new headless mode (better CDP support)
                            # ─── ATTACH TO YOUR EXISTING CDP ───
                            remote_debug=True,    # Tells SB: don’t launch Chrome, use existing CDP
                            # https://peter.sh/experiments/chromium-command-line-switches/
                            chromium_arg=[
                                            "--no-sandbox",
                                            # "--disable-setuid-sandbox",
                                            "--disable-dev-shm-usage",
                                            # "--disable-gpu",
                                            # "--disable-software-rasterizer"
                                            "--remote-debugging-address=0.0.0.0",
                                            "--remote-debugging-port=9333",
                                            ],

                            # pls="none",
                            # use_auto_ext=False,       # Disable automation extensions
                            # disable_csp=True,         # Disable Content Security Policy
                            # incognito=True,           # Use incognito mode
                              maximize=True, timeout_multiplier=3, save_screenshot=True,) as sb):
            try:
                logger.info(f"Starting Decolar Selenium process with params: {params}")
                url = 'https://www.decolar.com/hoteis'
                sb.activate_cdp_mode()
                tab = sb.cdp.page
                self.requests_handle.listenXHR(tab)
                sb.open(url)
                sb.sleep(2.5)


                sb.internalize_links()  # Don't open links in a new tab

                # 1) Inject override
                sb.execute_script("""
                  window._navigatedUrl = null;
                  const shims = [
                    ['open', window.open],
                    ['assign', location.assign],
                    ['replace', location.replace]
                  ];
                  for (const [name, fn] of shims) {
                    const parts = name === 'open' ? [window, fn] : [location, fn];
                    const obj = parts[0], orig = parts[1];
                    obj[name] = function(url, ...args) {
                      window._navigatedUrl = url;
                      return orig.call(this, url, ...args);
                    };
                  }
                """)

                # logger.info(f"Driver: {sb.driver}")
                # logger.info(f"CDP driver: {sb.cdp}")

                logger.info(f"Opening URL: {url}")
                # self.print_browser_info(sb)
                logger.info(f"After Browser info")

                self.save_screenshot("home", driver=sb)

                # self.close_login_incentive(sb)

                def location_part():
                    logger.info(f"Entering location: {location}")
                    # Enter Location
                    # location_btn
                    location_selector = "input[placeholder*='Insira uma cidade, hospedagem ou ponto de interesse']"
                    # sb.cdp.gui_click_element(location_selector)
                    sb.cdp.mouse_click(location_selector)
                    sb.sleep(2)

                    # for char in location:
                    #     sb.cdp.press_keys(location_selector, char)
                    #     time.sleep(0.5)  # Adjust delay as needed
                    # sb.cdp.press_keys(location_selector, "\n")
                    # sb.sleep(3)
                    # sb.cdp.type(location_selector, location)
                    # sb.sleep(2)
                    # sb.cdp.set_value(location_selector, location)
                    # sb.sleep(2)
                    # sb.cdp.send_keys(location_selector, location + "\n")
                    # sb.sleep(2)
                    # sb.cdp.press_keys(location_selector, location)
                    # sb.sleep(2)
                    # sb.cdp.send_keys(location_selector, Keys.ARROW_DOWN)
                    # sb.sleep(2)
                    # sb.cdp.send_keys(location_selector, Keys.ENTER)
                    # sb.sleep(2)

                    # # sb.cdp.focus(location_selector)
                    # sb.cdp.gui_press_keys(location)
                    # sb.sleep(2)

                    sb.cdp.evaluate(f'''
                        const input = document.querySelector("{location_selector}");

                        // Clear any existing value
                        input.value = "";

                        // Set the new value character by character to trigger suggestions
                        const locationText = "{location}";  // Changed variable name to avoid collision
                        for (let i = 0; i < locationText.length; i++) {{
                            input.value += locationText[i];

                            // Dispatch events that would normally happen during typing
                            input.dispatchEvent(new InputEvent('input', {{bubbles: true}}));
                            input.dispatchEvent(new KeyboardEvent('keydown', {{key: locationText[i], bubbles: true}}));
                            input.dispatchEvent(new KeyboardEvent('keypress', {{key: locationText[i], bubbles: true}}));
                            input.dispatchEvent(new KeyboardEvent('keyup', {{key: locationText[i], bubbles: true}}));
                        }}

                        // Trigger final events to ensure suggestions appear
                        input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        input.dispatchEvent(new Event('focus', {{ bubbles: true }}));
                    ''')
                    sb.sleep(2)

                    # text_to_type = "Hello, CDP World!"
                    # for char in text_to_type:
                    #     # Dispatch keyDown event for the character
                    #     keydown_event = {
                    #         "type": "keyDown",
                    #         "key": char,
                    #         "text": char,
                    #         "code": char,
                    #         "windowsVirtualKeyCode": ord(char.upper()) if char.isalpha() else 0,
                    #         "nativeVirtualKeyCode": ord(char.upper()) if char.isalpha() else 0
                    #     }
                    #     sb.driver.execute_cdp_cmd("Input.dispatchKeyEvent", keydown_event)
                    #
                    #     # Dispatch keyUp event for the character
                    #     keyup_event = {
                    #         "type": "keyUp",
                    #         "key": char,
                    #         "text": char,
                    #         "code": char,
                    #         "windowsVirtualKeyCode": ord(char.upper()) if char.isalpha() else 0,
                    #         "nativeVirtualKeyCode": ord(char.upper()) if char.isalpha() else 0
                    #     }
                    #     sb.driver.execute_cdp_cmd("Input.dispatchKeyEvent", keyup_event)

                    # # Dispatch an Arrow Down key press using CDP
                    # arrow_down_keydown = {
                    #     "type": "keyDown",
                    #     "key": "ArrowDown",
                    #     "code": "ArrowDown",
                    #     "windowsVirtualKeyCode": 40,
                    #     "nativeVirtualKeyCode": 40,
                    # }
                    # sb.driver.execute_cdp_cmd("Input.dispatchKeyEvent", arrow_down_keydown)
                    #
                    # arrow_down_keyup = {
                    #     "type": "keyUp",
                    #     "key": "ArrowDown",
                    #     "code": "ArrowDown",
                    #     "windowsVirtualKeyCode": 40,
                    #     "nativeVirtualKeyCode": 40,
                    # }
                    # sb.driver.execute_cdp_cmd("Input.dispatchKeyEvent", arrow_down_keyup)

                    # # Type location character by character with natural timing variations
                    # for char in location:
                    #     # Add random timing variation to appear more human-like
                    #     delay = round(random.uniform(0.45, 0.95), 2)
                    #
                    #     # Simulate realistic keypress events that will trigger JavaScript listeners
                    #     sb.cdp.evaluate(f"""
                    #         const input = document.querySelector('{location_selector}');
                    #         const lastValue = input.value;
                    #         input.value = lastValue + '{char}';
                    #
                    #         // Create and dispatch events that most autocomplete systems listen for
                    #         input.dispatchEvent(new KeyboardEvent('keydown', {{ key: '{char}', bubbles: true }}));
                    #         input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    #         input.dispatchEvent(new KeyboardEvent('keyup', {{ key: '{char}', bubbles: true }}));
                    #     """)
                    #     time.sleep(delay)

                    # Wait for autocomplete suggestions to appear
                    sb.sleep(1.5)

                    # sb.cdp.mouse_click(".sbox5-title-closed-packages")
                    # sb.sleep(.2)

                    # sb.cdp.click(location_selector)
                    # sb.sleep(1)
                    input_element_selection_xpath = f".ac-wrapper.-show .ac-container li"
                    suggestion = sb.cdp.find_element(
                        input_element_selection_xpath,
                        timeout=30
                    )
                    suggestion.mouse_click()
                    sb.sleep(1)

                location_part()

                def calendar_part():
                    # self.close_login_incentive(sb)
                    logger.info(f"Selecting dates: {start_date} to {end_date}")

                    # Enter Dates
                    date_button_selector = "[placeholder*='Entrada'], [placeholder*='Check in'], [placeholder*='Saída']"
                    sb.cdp.click(date_button_selector)
                    sb.sleep(1)

                    prev_btn = sb.cdp.find_element("a[class*='calendar-arrow-left']")
                    next_btn = sb.cdp.find_element("a[class*='calendar-arrow-right']")

                    month_left, month_right = self.get_months_container(sb)

                    month_label_selector = ".sbox5-monthgrid-title"
                    month_left_label = month_left.query_selector(month_label_selector)
                    start_date_text = month_left_label.text
                    cal_start_month_name = start_date_text.split()[0]

                    portuguese_to_english = {
                        'janeiro': 'January', 'fevereiro': 'February', 'março': 'March',
                        'abril': 'April', 'maio': 'May', 'junho': 'June',
                        'julho': 'July', 'agosto': 'August', 'setembro': 'September',
                        'outubro': 'October', 'novembro': 'November', 'dezembro': 'December'
                    }

                    cal_start_month_name = portuguese_to_english.get(cal_start_month_name.lower(),
                                                                     cal_start_month_name.lower()).lower()
                    cal_start_month_number = datetime.datetime.strptime(cal_start_month_name, "%B").month
                    year = int(start_date_text.split()[-1])

                    # Navigate to the correct month
                    while not (start_year == year and start_date.month == cal_start_month_number):
                        if start_year < year and start_date.month < cal_start_month_number:
                            prev_btn.click()
                        elif start_year > year or start_date.month > cal_start_month_number:
                            next_btn.click()
                        sb.sleep(1)

                        month_left, month_right = self.get_months_container(sb)
                        try:
                            month_left_label = month_left.query_selector(month_label_selector)
                        except:
                            logger.error(f'Element not found or webpage not loaded in time: {month_label_selector}')
                            sb.save_screenshot("calendar_error")
                            raise Exception(f'Element not found or webpage not loaded in time: {month_label_selector}')

                        start_date_text = month_left_label.text
                        cal_start_month_name = start_date_text.split()[0]
                        cal_start_month_name = portuguese_to_english.get(cal_start_month_name.lower(),
                                                                         cal_start_month_name.lower()).lower()
                        cal_start_month_number = datetime.datetime.strptime(cal_start_month_name, "%B").month
                        year = int(start_date_text.split()[-1])

                    # Select start date
                    if start_date.month == cal_start_month_number and start_year == year:
                        # Find day elements in the left month
                        day_elements = month_left.query_selector_all(".sbox5-monthgrid-datenumber-number")
                        start_day_found = False

                        for day_element in day_elements:
                            if int(day_element.text.strip()) == start_day:
                                day_element.click()
                                start_day_found = True
                                sb.sleep(1)
                                break

                        if not start_day_found:
                            logger.error(f"Start day element not found: {start_day}")
                            sb.save_screenshot("start_day_error")
                            raise Exception(f"Start day element not found: {start_day}")

                    # Get updated month containers
                    month_left, month_right = self.get_months_container(sb)

                    # Select end date with similar approach
                    if end_month.lower() in cal_start_month_name.lower() and end_year == year:
                        # Find day elements in the left month
                        day_elements = month_left.query_selector_all(".sbox5-monthgrid-datenumber-number")
                        end_day_found = False

                        for day_element in day_elements:
                            if int(day_element.text.strip()) == end_day:
                                day_element.click()
                                end_day_found = True
                                sb.sleep(1)
                                break

                        if not end_day_found:
                            logger.debug(f'End day element not found in left month: {end_day}')
                    else:
                        # Find day elements in the right month
                        day_elements = month_right.query_selector_all(".sbox5-monthgrid-datenumber-number")
                        end_day_found = False

                        for day_element in day_elements:
                            if int(day_element.text.strip()) == end_day:
                                day_element.click()
                                end_day_found = True
                                sb.sleep(1)
                                break

                        if not end_day_found:
                            logger.debug(f'End day element not found in right month: {end_day}')

                    sb.sleep(1)

                    # Click the "Apply" button
                    calendar_done_selector = ".calendar-footer button:contains('Aplicar'), .calendar-footer button:nth-child(2)"
                    try:
                        sb.cdp.click(calendar_done_selector)
                    except:
                        logger.error(f'Calendar done button not found: {calendar_done_selector}')
                        sb.save_screenshot("calendar_done_error")
                        raise Exception(f'Calendar done button not found: {calendar_done_selector}')
                    sb.sleep(1)

                calendar_part()

                # self.close_login_incentive(sb)

                def rooms_part():
                    logger.info(f"Entering room and guest details: {adults} adults, {children} children")
                    # Enter Guests
                    # guest_field
                    room_selector = f"[class*='distributionPassengers']"
                    sb.cdp.mouse_click(room_selector)
                    sb.sleep(1)

                    room_controls_selector = "[class*='stepper__room'] [class*='stepper__distribution_container'] > div"
                    room_controls = sb.cdp.select_all(room_controls_selector)
                    adults_input_selector = "input[class*='steppers-tag']"
                    adults_input = room_controls[0].query_selector(adults_input_selector)
                    current_adults = int(adults_input.text)

                    remove_btn = room_controls[0].query_selector("button")
                    add_btn = room_controls[0].query_selector_all("button")[1]

                    while current_adults != adults:
                        if current_adults < adults:
                            add_btn.click()
                        else:
                            remove_btn.click()
                        sb.sleep(1)
                        adults_input = room_controls[0].query_selector(adults_input_selector)
                        current_adults = int(adults_input.text)

                    if children > 0:
                        add_child_btn = room_controls[1].query_selector_all("button")[1]
                        for _ in range(children):
                            add_child_btn.mouse_click()
                            sb.sleep(1)

                        # Find all select elements matching the selector
                        age_selects = sb.find_elements(f"select[aria-label*='Idade do menor']")

                        # Iterate over the first, second, and third select elements
                        for index, select in enumerate(age_selects):  # Limit to first three elements
                            # Use SeleniumBase to select option by value for each element
                            sb.select_option_by_value(f"select[aria-label*='Idade do menor']:nth-child({index+1})", "10")
                            sb.sleep(0.5)  # Pause to ensure the action completes
                            sb.cdp.mouse_click(room_selector)
                            sb.sleep(0.5)

                    # guest_done
                    sb.cdp.click("[class*='stepper__room__footer'] > button:nth-child(2)")
                    sb.sleep(1)

                rooms_part()

                logger.info(f"Clicking search button")
                # Search
                # search_btn
                sb.cdp.click("button[class*='sbox5-box-button-ovr']")
                sb.sleep(random.uniform(3.0, 5.0))

                try:
                    continue_brazil_selector = "a[class*='wrong-country-modal-stay']"
                    sb.cdp.wait_for_element_visible(continue_brazil_selector, timeout=10)
                    sb.cdp.click(continue_brazil_selector)
                    sb.sleep(2)
                    logger.info(f"Clicked continue Brazil button")
                except NoSuchElementException as e:
                    logger.debug(f"Continue Brazil button not found: {str(e)}")
                except Exception as e:
                    logger.error(f"Error clicking continue Brazil button: {str(e)}")
                    # self.save_screenshot("continue_brazil_error", driver=sb)

                sb.sleep(random.uniform(0.5, 2.0))

                self.select_currency_process(sb)

                self.close_login_incentive(sb)

                self.save_screenshot("search_results", driver=sb)

                logger.info(f"Waiting for property results to load")

                property_results_selector = "aloha-list-view-container > ul > li"
                sb.cdp.wait_for_element_visible(property_results_selector, timeout=30)
                logger.info(f"Property results to loaded")
                for i in range(10):
                    # sb.cdp.scroll_down(8)
                    sb.cdp.gui_press_key("pgdn")
                    logger.info(f"Scrolling down to load more results: {i+1}/10")
                    sb.sleep(.1)
                # sb.sleep(2)
                # sb.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                # sb.sleep(1)

                # self.close_login_incentive(sb)

                logger.info(f"Selecting all hotel cards with selector: {property_results_selector}")

                # Find hotel
                hotel_cards = sb.cdp.select_all(property_results_selector, timeout=30)

                # logger.info(f"Found hotel cards on the page: {hotel_cards}")

                if not hotel_cards:
                    logger.error("No hotel cards found on the page.")
                    self.save_screenshot("no_hotel_cards", driver=sb)
                    return {
                        "success": False,
                        "error": "No hotel cards found",
                        "search_criteria": params,
                        "hotel": params.get('location'),
                        "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
                    }

                found = False
                for card in hotel_cards:
                    if "This property has no availability on our site".lower() in card.text.lower():
                        return {
                            "success": True,
                            "error": "This property has no availability",
                            "search_criteria": params,
                            "hotel": params.get('location'),
                            "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
                        }
                    if location.lower() in card.text.lower():
                        logger.info(f"Found hotel card: {card}")
                        self.save_screenshot("hotel_card", driver=sb)

                        sb.sleep(random.uniform(0.5, 2.0))
                        card.scroll_into_view()
                        sb.sleep(random.uniform(0.5, 2.0))
                        # logger.info(f"Clicking on hotel card for location: {location}")
                        # card.click()
                        # card.mouse_click()
                        # card.gui_click()
                        # logger.info(f"Clicked hotel card for location: {location}")

                        logger.info(f"Clicking availability button for hotel: {location}")
                        # avail_button = card.query_selector("[class*='accommodation-name']")
                        avail_selector = "aloha-button"
                        avail_button = card.query_selector(avail_selector)
                        logger.info(f"Availability button found: {avail_button}")
                        # avail_button.mouse_move()
                        # avail_button.focus()
                        # sb.sleep(random.uniform(0.5, 2.0))
                        # sb.reconnect()
                        # avail_button.mouse_click()
                        # avail_button.click()
                        # avail_button.gui_click()
                        # sb.cdp.click(f"{property_results_selector} aloha-button")

                        # THIS WORKS TO GET THE RESPONSE BODY
                        # # Before clicking, set up comprehensive request monitoring
                        # sb.execute_script("""
                        #   window._hermesResponse = null;
                        #   window._capturedRequests = [];
                        #
                        #   // Enhanced fetch override with response capture
                        #   const originalFetch = window.fetch;
                        #   window.fetch = function(...args) {
                        #     const request = originalFetch.apply(this, args);
                        #
                        #     if (args[0] && args[0].includes('hermes-service/topic/accommodations_cluster_selection')) {
                        #       console.log('Hermes fetch intercepted:', args[0]);
                        #       request.then(response => {
                        #         return response.clone().text().then(body => {
                        #           window._hermesResponse = {
                        #             url: args[0],
                        #             body: body,
                        #             status: response.status
                        #           };
                        #           console.log('Hermes response captured:', window._hermesResponse);
                        #         });
                        #       }).catch(err => console.error('Hermes fetch error:', err));
                        #     }
                        #
                        #     return request;
                        #   };
                        #
                        #   // Enhanced XHR override with response capture
                        #   const originalXHRSend = XMLHttpRequest.prototype.send;
                        #   XMLHttpRequest.prototype.send = function(data) {
                        #     if (this._url && this._url.includes('hermes-service/topic/accommodations_cluster_selection')) {
                        #       this.addEventListener('readystatechange', function() {
                        #         if (this.readyState === 4) {
                        #           window._hermesResponse = {
                        #             url: this._url,
                        #             body: this.responseText,
                        #             status: this.status
                        #           };
                        #           console.log('Hermes XHR response captured:', window._hermesResponse);
                        #         }
                        #       });
                        #     }
                        #     return originalXHRSend.call(this, data);
                        #   };
                        #
                        #   const originalXHROpen = XMLHttpRequest.prototype.open;
                        #   XMLHttpRequest.prototype.open = function(method, url, ...args) {
                        #     this._url = url;
                        #     return originalXHROpen.call(this, method, url, ...args);
                        #   };
                        # """)

                        # grab the real <button> inside the <aloha-button>
                        inner_btn = avail_button.query_selector("button")
                        # physically move & click
                        inner_btn.mouse_move()
                        sb.sleep(0.2)
                        inner_btn.mouse_click()

                        # # THIS WORKS TO GET THE RESPONSE BODY
                        # # Wait and check for captured hermes response
                        # for attempt in range(30):  # 30 seconds timeout
                        #     sb.sleep(1)
                        #     hermes_response = sb.execute_script("return window._hermesResponse")
                        #
                        #     if hermes_response:
                        #         logger.info(f"Hermes response captured: {hermes_response}")
                        #         try:
                        #             response_data = json.loads(hermes_response['body'])
                        #             target_url = response_data.get('url') or response_data.get('redirect_url')
                        #             if target_url:
                        #                 logger.info(f"Navigating to: {target_url}")
                        #                 sb.cdp.open(target_url)
                        #                 break
                        #         except Exception as e:
                        #             logger.error(f"Error parsing hermes response: {e}")
                        #         break
                        #
                        #     if attempt == 29:
                        #         logger.warning("No hermes-service response captured after 30 seconds")


                        # # Check for captured requests
                        # captured_requests = sb.execute_script("return window._capturedRequests")
                        # hermes_url = sb.execute_script("return window._navigatedUrl")
                        # print("Captured requests:", captured_requests)
                        # print("Navigation URL:", hermes_url)

                        # # 3) Read back what was passed to window.open()
                        # new_tab_url = sb.execute_script("return window._navigatedUrl")
                        # print("Would have opened:", new_tab_url)

                        # 3. Focus then press Enter/Space
                        # avail_button.focus()
                        # avail_button.send_keys("\r")  # Enter key
                        # or
                        # avail_button.send_keys(" ")  # Space key
                        # avail_button.press_keys("\r")
                        # sb.cdp.evaluate(f"document.querySelector('aloha-button').dispatchEvent(new Event('click'))")

                        # sb.cdp.bring_active_window_to_front()
                        # sb.cdp.click("aloha-button", timeout=10)

                        # sb.cdp.evaluate(f'''
                        #             (function() {{
                        #                 const button = document.querySelector("{property_results_selector} {avail_selector}");
                        #                 const linkElement = button.closest('a') || button.querySelector('a');
                        #                 if (linkElement && linkElement.href) {{
                        #                     window.open(linkElement.href, '_blank');
                        #                 }} else {{
                        #                     button.click();
                        #                 }}
                        #             }})();
                        #         ''')

                        # sb.cdp.switch_to_newest_tab()
                        # sb.sleep(random.uniform(3.0, 5.0))
                        # self.save_screenshot("new_tab", driver=sb)

                        logger.info(f"Clicked availability button for hotel: {location}")

                        # # More human-like interaction approach
                        # try:
                        #     # First try: Look for a direct link instead of clicking accommodation name
                        #     link_element = card.query_selector("a[href*='hotel'], a[href*='accommodation']")
                        #     if link_element:
                        #         # Navigate directly instead of clicking to avoid new tab
                        #         hotel_url = link_element.get_attribute("href")
                        #         sb.cdp.open(hotel_url)
                        #     else:
                        #         # Fallback: More natural click behavior
                        #         avail_button = card.query_selector("[class*='accommodation-name']")
                        #
                        #         # Add random mouse movement and timing
                        #         sb.cdp.evaluate(f'''
                        #                 const element = document.querySelector("[class*='accommodation-name']");
                        #                 if (element) {{
                        #                     // Simulate mouse hover first
                        #                     element.dispatchEvent(new MouseEvent('mouseover', {{bubbles: true}}));
                        #
                        #                     // Add slight delay
                        #                     setTimeout(() => {{
                        #                         // Right-click to open context menu (more human-like)
                        #                         element.dispatchEvent(new MouseEvent('contextmenu', {{bubbles: true}}));
                        #
                        #                         // Then left-click
                        #                         setTimeout(() => {{
                        #                             element.click();
                        #                         }}, {random.randint(200, 500)});
                        #                     }}, {random.randint(300, 700)});
                        #                 }}
                        #             ''')
                        #
                        # except Exception as e:
                        #     logger.error(f"Error clicking accommodation: {e}")
                        #     # Last resort: try different selector
                        #     try:
                        #         card.mouse_click()
                        #     except:
                        #         raise Exception(f"Could not click accommodation for {location}")
                        #

                        # card.mouse_click()
                        # sb.sleep(2)
                        # sb.cdp.evaluate(f'''
                        #     const card = document.evaluate(`//*[contains(text(), "${location}")]`, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                        #     if (card) {{
                        #         card.scrollIntoView({{behavior: "smooth", block: "center"}});
                        #
                        #         // Create and dispatch click events
                        #         const clickEvent = new MouseEvent('click', {{
                        #             bubbles: true,
                        #             cancelable: true,
                        #             view: window
                        #         }});
                        #         card.dispatchEvent(clickEvent);
                        #     }}
                        # ''')
                        # sb.cdp.evaluate(f'''
                        #     // Try multiple approaches to find the hotel card
                        #     function findHotelCard() {{
                        #         // First try: Search by text content in the hotel cards container
                        #         const cards = document.querySelectorAll("aloha-list-view-container > ul > li");
                        #         for (const card of cards) {{
                        #             if (card.textContent.toLowerCase().includes("{location.lower()}")) {{
                        #                 return card;
                        #             }}
                        #         }}
                        #
                        #         // Second try: Look for accommodation name elements
                        #         const nameElements = document.querySelectorAll('[class*="accommodation-name"], [class*="hotel-name"], .name');
                        #         for (const elem of nameElements) {{
                        #             if (elem.textContent.toLowerCase().includes("{location.lower()}")) {{
                        #                 return elem.closest('li') || elem;
                        #             }}
                        #         }}
                        #
                        #         // Third try: XPath as fallback
                        #         return document.evaluate(`//li[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), "{location.lower()}")]`,
                        #             document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                        #     }}
                        #
                        #     let result = false;
                        #     const card = findHotelCard();
                        #     if (card) {{
                        #         card.scrollIntoView({{behavior: "smooth", block: "center"}});
                        #
                        #         // Find the clickable element
                        #         const clickTarget = card.querySelector('a, button, [role="button"]') || card;
                        #
                        #         // Create and dispatch click events immediately
                        #         const clickEvent = new MouseEvent('click', {{
                        #             bubbles: true,
                        #             cancelable: true,
                        #             view: window
                        #         }});
                        #         clickTarget.dispatchEvent(clickEvent);
                        #
                        #         // As a fallback, try a regular click
                        #         try {{ clickTarget.click(); }} catch(e) {{}}
                        #
                        #         result = true;
                        #     }}
                        #     result; // This will be returned as the result of evaluate()
                        # ''')
                        sb.sleep(random.uniform(3.0, 5.0))
                        found = True
                        break

                if not found:
                    raise Exception(f"Hotel not found for location: {location}")
                # sb.cdp.evaluate("window.open('URL', '_blank')")
                self.save_screenshot("tabs", driver=sb)

                # sb.reconnect()
                # sb.cdp.open_new_tab(url="https://www.google.com/")

                nav_history = sb.cdp.get_navigation_history()
                logger.info(f"Navigation history: {nav_history}")

                filtered_requests = []
                loop = sb.cdp.get_event_loop()
                xhr_responses = loop.run_until_complete(self.requests_handle.receiveXHR(tab))
                for response in xhr_responses:
                    logger.debug("*** ==> XHR Request URL <== ***")
                    logger.debug(f'{response["url"]}')
                    is_base64 = response["is_base64"]
                    b64_data = "Base64 encoded data"
                    try:
                        headers = ast.literal_eval(response["body"])["headers"]
                        logger.debug("*** ==> XHR Response Headers <== ***")
                        logger.debug(headers if not is_base64 else b64_data)
                    except Exception:
                        response_body = response["body"]
                        logger.debug("*** ==> XHR Response Body <== ***")
                        logger.debug(response_body if not is_base64 else b64_data)

                # sb.disconnect()
                # sb.connect()
                logger.debug(f"Tabs opened before closing: {len(sb.cdp.get_tabs())} - {sb.cdp.get_tabs()}")

                # for window in sb.driver.window_handles:
                #     sb.switch_to_window(window)
                #     logger.info(f"Switching to window url: {sb.get_current_url()}")
                #     if "/accommodations/detail" in sb.get_current_url():
                #         break

                while len(sb.cdp.get_tabs()) > 1:
                    sb.cdp.close_active_tab()
                    sb.cdp.switch_to_newest_tab()
                    # self.save_screenshot("tab_closed", driver=sb)
                    sb.sleep(0.6)

                sb.sleep(1)

                # current_url = sb.cdp.get_current_url()
                # sb.cdp.open_new_window()
                # sb.cdp.switch_to_newest_tab()
                # sb.cdp.open(current_url)

                # sb.cdp.go_back()
                # sb.sleep(1)
                # sb.cdp.go_forward()
                # sb.sleep(1)
                # sb.cdp.reload(ignore_cache=True, script_to_evaluate_on_load=None)
                # sb.sleep(5)

                # self.select_currency_process(sb)

                # tab = sb.cdp.page
                # tab = sb.cdp.get_active_tab()
                # self.requests_handle.listenXHR(tab)

                logger.debug(f"Tabs opened: {len(sb.cdp.get_tabs())} - {sb.cdp.get_tabs()}")

                current_url = None
                # current_url = sb.cdp.get_current_url()
                currency = 'USD'
                response = {
                    "success": True,

                    "search_criteria": params,

                    "hotel": params.get('location'),
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
                }

                self.save_screenshot("hotel_details", driver=sb)

                rooms_table_selector = "aloha-roompacks-grid-container aloha-roompacks-group-container"
                sb.cdp.wait_for_element_visible(rooms_table_selector, timeout=30)
                rooms = []
                all_rooms = sb.cdp.select_all(rooms_table_selector)
                block_ids = []
                for room in all_rooms:
                    # room = all_rooms.query_selector(f'{room_child.attrs.class_.replace(" ", ".")}')
                    room.scroll_into_view()

                    sb.sleep(0.5)

                    # block_id = room.get_attribute("data-block-id")
                    # if block_id in block_ids:
                    #     logger.info(f"Skipping block {block_id}")
                    #     continue
                    # block_ids.append(block_id)

                    # price_element = room.query_selector('[class="eva-3-p -eva-3-tc-gray-0 -eva-3-mt-sm additional-caption-message focused-message"]') # per night
                    # price_element = room.query_selector('[class="main-value"]') # total nights
                    # if not price_element:
                    #     logger.debug(f"No price found for room {room}")
                    #     continue
                    # price = re.sub(r'[^\d.,]', '', price_element.text).replace('.', '').replace(',', '.')
                    price = room.query_selector("aloha-summary-price [class='main-value']")
                    if price:
                        price = price.text.strip()

                    name = room.query_selector("aloha-room-type [class*='room-name']")
                    # if not name:
                    #     logger.info(f"Skipping block {block_id}")
                    #     continue
                    name = name.text.strip()
                    # beds = room.query_selector('[class*="bed-types-wrapper"]')
                    #
                    # if not beds:
                    #     beds = room.query_selector('[class="rt-bed-type"]')
                    # beds = beds.text.strip() if beds else "No beds info"

                    room = {
                        "name": name,
                        "beds": [],
                        "price": price,
                    }
                    rooms.append(room)

                # while True:
                #     # sb.cdp.scroll_down(1)
                #     sb.sleep(0.5)
                #
                #
                #     button_right_rooms = sb.cdp.find_element('nav.css-1elq7vm li:nth-child(5) button')
                #     is_disabled = button_right_rooms.get_attribute('disabled')
                #     if is_disabled == '':
                #         break
                #     else:
                #         button_right_rooms.scroll_into_view()
                #         button_right_rooms.click()
                #         sb.sleep(0.5)

                response['rooms'] = rooms
                response['rooms_found'] = rooms.__len__()
                response['currency_prices'] = currency

            except Exception as e:
                logger.error(f"Error during Decolar Selenium process: {str(e)}", traceback=traceback.format_exc())
                response['success'] = False
                response['error'] = f"{type(e).__name__}: {str(e)}"

        if current_url:
            with (seleniumbase.SB(uc=True, test=True, locale_code="en", ad_block=True, window_size='1920,1080', maximize=True,
                                  timeout_multiplier=3, save_screenshot=True) as sb):
                sb.activate_cdp_mode(current_url)
                sb.sleep(2.5)

                sb.cdp.open(current_url)

                tab = sb.cdp.page
                self.requests_handle.listenXHR(tab)

                # sb.sleep(2)
                time.sleep(2)
                for i in range(10):
                    sb.cdp.scroll_down(18)

                response = self.process_requests(sb, tab)
        else:
            logger.debug(f"Tab not found")

        return response

    def print_browser_info(self, sb=None):
        """Print Chrome version, driver version, and user agent."""
        if sb:
            logger.info(f"Using SeleniumBase instance to get browser info")
            # For seleniumbase implementation
            try:
                chrome_version = sb.cdp.evaluate("navigator.userAgent")
                logger.info(f"Getting browser info with SeleniumBase (SB): {chrome_version}")
                user_agent = chrome_version
                driver_version = sb.driver.capabilities.get('chrome', {}).get('chromedriverVersion', 'Unknown')

                logger.info(f"Chrome version: {chrome_version}")
                logger.info(f"Driver version: {driver_version}")
                logger.info(f"User Agent: {user_agent}")
            except Exception as e:
                logger.error(f"Error getting browser info with SB: {str(e)}")
        else:
            logger.info(f"Using Selenium driver instance to get browser info")
            # For regular selenium implementation
            try:
                chrome_version = self.driver.capabilities.get('browserVersion', 'Unknown')
                driver_version = self.driver.capabilities.get('chrome', {}).get('chromedriverVersion', 'Unknown')
                user_agent = self.driver.execute_script("return navigator.userAgent;")

                logger.info(f"Chrome version: {chrome_version}")
                logger.info(f"Driver version: {driver_version}")
                logger.info(f"User Agent: {user_agent}")
            except Exception as e:
                logger.error(f"Error getting browser info: {str(e)}")

    def process_requests(self, sb, tab):
        response = {}
        # logger.debug(f"{len(sb.cdp.get_tabs())} - {sb.cdp.get_window()}")
        filtered_requests = []
        loop = sb.cdp.get_event_loop()
        xhr_responses = loop.run_until_complete(self.requests_handle.receiveXHR(tab))
        for response in xhr_responses:
            logger.debug("*** ==> XHR Request URL <== ***")
            logger.debug(f'{response["url"]}')
            # is_base64 = response["is_base64"]
            # b64_data = "Base64 encoded data"
            # try:
            #     headers = ast.literal_eval(response["body"])["headers"]
            #     logger.debug("*** ==> XHR Response Headers <== ***")
            #     logger.debug(headers if not is_base64 else b64_data)
            # except Exception:
            #     response_body = response["body"]
            #     logger.debug("*** ==> XHR Response Body <== ***")
            #     logger.debug(response_body if not is_base64 else b64_data)
            if ('/graphql' in response["url"]
                    and response.get("body") and 'propertyOffers' in response["body"]):
                filtered_requests.append(response)

        logger.debug(f"requests found: {filtered_requests.__len__()} out of {len(xhr_responses)}")

        data_found = False
        if filtered_requests.__len__() == 1:
            response = filtered_requests[0]

            # Parse the request body as JSON
            body = json.loads(response["body"])

            # if body is a list get the first element
            if isinstance(body, list):
                body = body[0]

            response = self.standardize_data(body)

            data_found = True
            logger.debug(f"Request URL: {response['url']}")

        if not data_found:
            self.save_screenshot(driver=sb)
            raise Exception(f"Data not found")

        ##
        # prefilt = [req for req in sb.driver.requests if '/graphql' in req.path]
        # filtered_requests = [req for req in prefilt if
        #                      json.loads(req.body).get('operationName', '').lower() == 'ancillarypropertyoffersquery']
        #
        # if filtered_requests and filtered_requests[0].response:
        #     response_body = filtered_requests[0].response.body.decode('utf-8')
        #     body = json.loads(response_body)
        #
        #     if isinstance(body, list):
        #         body = [b for b in body if
        #                 b.get('data', {}).get('propertyOffers', {'loading': {}}).get('loading') is None]
        #         body = body[0] if body else {}
        #
        #     if "data" in body and "propertyOffers" in body['data']:
        #         response = self.standardize_data(body)
        #     else:
        #         raise Exception("Data not found")
        # else:
        #     raise Exception("No valid GraphQL response found")

        return response

    def close_login_incentive(self, sb=None):
        """Close the login incentive popup if present."""
        try:
            # Using CDP mode
            close_login_incentive_selector = "div[class*='login-incentive--button-close']"
            sb.cdp.mouse_click(close_login_incentive_selector, timeout=10)
        except Exception as e:
            logger.debug(f"Login incentive not found or couldn't be closed: {str(e)}")

    def select_currency_process(self, sb):
        # currency_btn
        """Select USD currency."""
        sb.cdp.find_element("select:has(option[value='USD'], option[value='BRL'])", timeout=15).scroll_into_view()
        sb.sleep(1)
        sb.cdp.select_option_by_text("select:has(option[value='USD'], option[value='BRL'])", "Dólar")
        sb.sleep(2)

        # current_url = sb.cdp.get_current_url()
        # if '?' in current_url:
        #     if 'currency=' in current_url:
        #         # Replace existing currency parameter
        #         import re
        #         current_url = re.sub(r'currency=[A-Z]{3}', 'currency=USD', current_url)
        #     else:
        #         # Add currency parameter
        #         current_url += '&currency=USD'
        # else:
        #     # Add currency parameter as first parameter
        #     current_url += '?currency=USD'
        #
        # # Navigate to the updated URL
        # sb.cdp.open(current_url)
        # sb.sleep(2)


        # try:
        #     # Get current URL
        #     current_url = sb.cdp.get_current_url()
        #
        #     # Check if URL already has parameters
        #     if '?' in current_url:
        #         if 'currency=' in current_url:
        #             # Replace existing currency parameter
        #             new_url = current_url.replace(
        #                 re.search(r'currency=[A-Z]{3}', current_url).group(0),
        #                 'currency=USD'
        #             )
        #         else:
        #             # Add currency parameter
        #             new_url = current_url + '&currency=USD'
        #     else:
        #         # Add currency parameter as first parameter
        #         new_url = current_url + '?currency=USD'
        #
        #     # Navigate to the new URL
        #     sb.cdp.open(new_url)
        #     sb.sleep(2)
        # except Exception as e:
        #     logger.debug(f"Could not set currency via URL: {str(e)}. Falling back to dropdown selection.")
        #     # Fallback to original method
        #     sb.cdp.select_option_by_text("select:has(option[value='USD'], option[value='MXN'])", "Dólar", timeout=10)
        #     sb.sleep(2)

        # try:
        #     # Find the select element
        #     select_element = sb.cdp.find_element("select:has(option[value='USD'], option[value='BRL'])", timeout=10)
        #
        #     # Click the select element to open the dropdown
        #     select_element.mouse_click()
        #     sb.sleep(1)
        #
        #     # Find the USD/Dólar option
        #     option_selector = "option[value='USD'], option:contains('Dólar')"
        #     dolar_option = sb.cdp.find_element(option_selector, timeout=5)
        #
        #     # Get coordinates and click on the option
        #     dolar_option.scroll_into_view()
        #     dolar_option.mouse_click()
        #     sb.sleep(2)
        #
        #     # Alternative approach using JavaScript if the above doesn't work
        #     if not dolar_option:
        #         sb.cdp.evaluate('''
        #               const select = document.querySelector("select:has(option[value='USD'], option[value='BRL'])");
        #               const options = Array.from(select.options);
        #               const dolarOption = options.find(opt => opt.text.includes("Dólar") || opt.value === "USD");
        #               if (dolarOption) {
        #                   select.value = dolarOption.value;
        #                   select.dispatchEvent(new Event('change', {bubbles: true}));
        #               }
        #           ''')
        #         sb.sleep(2)
        # except Exception as e:
        #     logger.debug(f"Could not select currency via mouse: {str(e)}. Falling back to default selection.")
        #     # Fallback to original method
        #     sb.cdp.select_option_by_text("select:has(option[value='USD'], option[value='BRL'])", "Dólar")
        #     sb.sleep(2)

        # sb.cdp.wait_for_element_visible("select:has(option[value='USD'], option[value='MXN'])", timeout=10)
        # sb.sleep(2)
        # sb.cdp.evaluate('''
        #     // Find the select element that contains USD or MXN options
        #     const selectElement = document.querySelector("select:has(option[value='USD'], option[value='MXN'])");
        #
        #     if (selectElement) {
        #         // Get all the options in the select element
        #         const options = Array.from(selectElement.options);
        #
        #         // Find the option that contains "Dólar" text
        #         const dolarOption = options.find(option => option.text.includes("Dólar"));
        #
        #         if (dolarOption) {
        #             // Select the Dólar option
        #             selectElement.value = dolarOption.value;
        #
        #             // Dispatch events to trigger any listeners
        #             selectElement.dispatchEvent(new Event('change', {bubbles: true}));
        #             selectElement.dispatchEvent(new Event('input', {bubbles: true}));
        #         }
        #     }
        # ''')
        # sb.sleep(2)

    def get_months_container(self, sb):
        calendar_container_selector = "[class*='calendar-container'] > div"
        calendar_container = sb.cdp.find_elements(calendar_container_selector)

        month_left = calendar_container[0]
        month_right = calendar_container[1]

        return month_left, month_right

    def standardize_data(self, data):
        return get_standard_data_second(data, self.params)


class DecolarSelenium(BaseSelenium):

    def __init__(self):
        super().__init__()

        self.name = 'decolar'

        # Only request URLs containing "despegar" or "whatever" will now be captured
        self.driver.scopes = [
            '.*decolar.*',
        ]

        self.params = {}

    def get_rooms(self, params):
        logger.debug(f'get_rooms: {params}')
        self.params = params

        website, region, location, start_day, start_month, start_year, end_day, end_month, end_year, adults, children, start_date, end_date = self.validate_input_data()

        # self.driver.execute_cdp_cmd("Runtime.disable", {})

        url = 'https://www.decolar.com/hoteis/'
        self.driver.get(url)

        self.random_wait()
        # self.driver.execute_script(
        #     f"""setTimeout(() => window.location.href="{url}", 100)""")
        # self.driver.service.stop()
        # self.driver.reconnect()

        logger.debug(f'url: {url}')

        def close_login_incentive():
            # close the login incentive
            close_login_incentive_xpath = f"//div[contains(@class, 'login-incentive--button-close')]"
            try:
                close_login_incentive = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, close_login_incentive_xpath)))
                close_login_incentive.location_once_scrolled_into_view
                close_login_incentive.click()
            except:
                print(f'Element not found or webpage not loaded in time: {close_login_incentive_xpath}')

        close_login_incentive()

        # *** Entering LOCATION ***
        def location_part():
            destination_form_field_xpath = f"//input[contains(@placeholder, 'Insira uma cidade') or contains(@placeholder, 'Ingresa una ciudad') or contains(@placeholder, 'Destino')" \
                                           f" or contains(@placeholder, 'Type a city') or contains(@placeholder, 'Destination')]"
            try:
                print(f'waiting for: {destination_form_field_xpath}')
                # Wait for actions to complete
                input_element = self.wait.until(EC.presence_of_element_located((By.XPATH, destination_form_field_xpath)))
            except:
                print(f'Element not found or webpage not loaded in time: {destination_form_field_xpath}')
                self.save_screenshot()
                raise Exception(f'Element not found or webpage not loaded in time: {destination_form_field_xpath}')

            print(f'entering keys for: {destination_form_field_xpath}')

            print(f'waiting to be clickable: {destination_form_field_xpath}')
            # Use JavaScript to change the autocomplete attribute to 'on'

            print(f'input_element: {input_element.text}')
            # Send keys to the input element
            input_element.click()
            # self.move_and_click(input_element)
            self.random_wait()
            input_element.send_keys(location)

            self.random_wait()

            input_element_selection_xpath = f"//*[contains(@class, 'ac-wrapper') and contains(@class, '-show')]//*[contains(@class, 'ac-container')]//li"
            try:
                input_element_selection = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, input_element_selection_xpath)))
            except:
                print(f'Element not found or webpage not loaded in time: {input_element_selection_xpath}')
                self.save_screenshot()
                raise Exception(f'Element not found or webpage not loaded in time: {input_element_selection_xpath}')
            input_element_selection[0].click()
            # self.move_and_click(input_element_selection[0])

            self.random_wait()

            input_element.send_keys(Keys.ENTER)

            # Simulate typing some words
            # self.driver.switch_to.active_element.send_keys(location)
            # # Simulate hitting the Enter key
            # self.driver.switch_to.active_element.send_keys(Keys.ENTER)

            self.random_wait()

        location_part()

        # *** Entering DATE ***
        def calendar_part():
            date_button_data_xpath = f"//*[contains(@placeholder, 'Entrada') or contains(@placeholder, 'Check in') or contains(@placeholder, 'Saída')]"
            print(f'preparing for: {date_button_data_xpath}')

            # Find the button using its data-stid attribute     and click it
            date_button = self.driver.find_element(By.XPATH, date_button_data_xpath)
            date_button.click()
            # self.move_and_click(date_button)

            self.random_wait()

            prev_button_month = self.driver.find_element(By.XPATH,
                                                         f"//a[contains(@class, 'calendar-arrow-left')]")
            next_button_month = self.driver.find_element(By.XPATH,
                                                         f"//a[contains(@class, 'calendar-arrow-right')]")

            calendar_container_path = f"//*[contains(@class,'calendar-container')]/div[contains(@class, 'sbox5-monthgrid')]"
            month_left = self.driver.find_elements(By.XPATH, calendar_container_path)[0]
            month_right = self.driver.find_elements(By.XPATH, calendar_container_path)[1]

            month_label_class = 'sbox5-monthgrid-title'
            month_left_label = month_left.find_element(By.XPATH, f".//*[contains(@class, '{month_label_class}')]")
            start_date_text = month_left_label.text
            cal_start_month_name = start_date_text.split()[0]
            # cal_start_month_name = month_left_label.find_element(By.CLASS_NAME, 'sbox5-monthgrid-title-month').text
            portuguese_to_english = {
                'janeiro': 'January',
                'fevereiro': 'February',
                'março': 'March',
                'abril': 'April',
                'maio': 'May',
                'junho': 'June',
                'julho': 'July',
                'agosto': 'August',
                'setembro': 'September',
                'outubro': 'October',
                'novembro': 'November',
                'dezembro': 'December'
            }
            cal_start_month_name = portuguese_to_english.get(cal_start_month_name.lower(), cal_start_month_name.lower()).lower()
            # Convert month name to month number using datetime module
            cal_start_month_number = datetime.datetime.strptime(cal_start_month_name, "%B").month
            year = int(start_date_text.split()[-1])
            # year = int(month_left_label.find_element(By.CLASS_NAME, 'sbox5-monthgrid-title-year').text)

            # iterate to the correct month
            while not (start_year == year and start_date.month == cal_start_month_number):
                # iterate to the next month or previous month
                if start_year < year and start_date.month < cal_start_month_number:
                    prev_button_month.click()
                    # self.move_and_click(prev_button_month)
                elif start_year > year or start_date.month > cal_start_month_number:
                    next_button_month.click()
                    # self.move_and_click(next_button_month)
                self.random_wait()

                month_left = self.driver.find_elements(By.XPATH, calendar_container_path)[0]
                month_right = self.driver.find_elements(By.XPATH, calendar_container_path)[1]

                try:
                    month_left_label = month_left.find_element(By.XPATH, f"//*[contains(@class, '{month_label_class}')]")
                except:
                    print(f'Element not found or webpage not loaded in time: {month_label_class}')
                    self.save_screenshot()
                    raise Exception(f'Element not found or webpage not loaded in time: {month_label_class}')

                start_date_text = month_left_label.text

                cal_start_month_name = start_date_text.split()[0]
                # cal_start_month_name = month_left_label.find_element(By.CLASS_NAME, 'sbox5-monthgrid-title-month').text
                cal_start_month_name = portuguese_to_english.get(cal_start_month_name.lower(),
                                                              cal_start_month_name.lower()).lower()
                cal_start_month_number = datetime.datetime.strptime(cal_start_month_name, "%B").month
                year = int(start_date_text.split()[-1])
                # year = int(month_left_label.find_element(By.CLASS_NAME, 'sbox5-monthgrid-title-year').text)

            # setting start date
            if start_date.month == cal_start_month_number and start_year == year:
                # select the start day
                # month_left.find_element(By.XPATH, f"//*[text()='{start_day}']").click()

                day_button = month_left.find_element(By.XPATH,
                                                     f".//*[contains(@class, 'sbox5-monthgrid-datenumber-number') and text()='{start_day}']")
                day_button.click()
                # self.move_and_click(day_button)
                self.random_wait()

            # setting end date

            month_left = self.driver.find_elements(By.XPATH, calendar_container_path)[0]
            month_right = self.driver.find_elements(By.XPATH, calendar_container_path)[1]

            # if the end date is in the left month of the calendar
            if end_month.lower() in cal_start_month_name.lower() and end_year == year:
                # select the end day
                try:
                    day_button = month_left.find_element(By.XPATH,
                                                         f".//*[contains(@class, 'sbox5-monthgrid-datenumber-number') and text()='{end_day}']")

                    day_button.click()
                    # self.move_and_click(day_button)
                    self.random_wait()
                except:
                    print(f'Element not found or webpage not loaded in time: {end_day}')
                    # if this gives error is because the date is already selected.

            else:
                try:
                    # we look in the right calendar month
                    day_button = month_right.find_elements(By.XPATH,
                                                           f".//*[contains(@class, 'sbox5-monthgrid-datenumber-number') and text()='{end_day}']")

                    if day_button.__len__() > 1:
                        day_button[1].click()
                        # self.move_and_click(day_button[1])
                    else:
                        day_button[0].click()
                        # self.move_and_click(day_button[0])
                    self.random_wait()
                except:
                    print(f'Element not found or webpage not loaded in time: {end_day}')
                    # if this gives error is because the date is already selected.

            calendar_done_button_xpath = "//div[contains(@class, 'calendar-footer')]//button[contains(text(), 'Aplicar')] | (//div[contains(@class, 'calendar-footer')]//button)[2]"
            try:
                calendar_done_button = self.driver.find_element(By.XPATH, calendar_done_button_xpath)
            except:
                print(f'Element not found or webpage not loaded in time: {calendar_done_button_xpath}')
                self.save_screenshot()
                raise Exception(f'Element not found or webpage not loaded in time: {calendar_done_button_xpath}')
            calendar_done_button.click()
            # self.move_and_click(calendar_done_button)
            self.random_wait()

        calendar_part()

        close_login_incentive()

        # *** Entering GUESTS ***
        def rooms_part():
            room_picker_data_xpath = f"//*[contains(@class, 'sbox5-3-first-input-wrapper') or contains(@class, 'sbox5-3-second-input-wrapper')]"
            try:
                button_room_picker = self.wait.until(EC.presence_of_element_located((By.XPATH, room_picker_data_xpath)))
            except:
                print(f'Element not found or webpage not loaded in time: {room_picker_data_xpath}')
                self.save_screenshot()
                raise Exception(f'Element not found or webpage not loaded in time: {room_picker_data_xpath}')

            button_room_picker.click()
            # self.move_and_click(button_room_picker)

            self.random_wait()

            room_controls_xpath = f"//div[@class='stepper__distribution_container']//*[@class='stepper__room__row']"
            room_controls = self.driver.find_elements(By.XPATH, room_controls_xpath)

            room_controls_footer_xpath = f"//div[contains(@class, 'distribution__container')]//*[contains(@class,'stepper__room__footer')]"
            room_controls_footer = self.driver.find_element(By.XPATH, room_controls_footer_xpath)

            # remove_adults_xpath = f".//descendant::button[1]"
            adults_input_xpath = f".//input[contains(@class, 'steppers-tag')]"
            # adults_input = self.wait.until(EC.presence_of_element_located((By.XPATH, adults_input_xpath)))
            adults_input = room_controls[0].find_elements(By.XPATH, adults_input_xpath)[0]

            # increase_adults_xpath = f".//descendant::button[2]"
            remove_adults_xpath = f".//button[contains(@class,'steppers-icon-left')]"
            increase_adults_xpath = f".//button[contains(@class,'steppers-icon-right')]"
            if adults and adults >= 1:
                current_adults = int(adults_input.get_attribute("value"))
                while current_adults != adults:
                    remove_adult_button = room_controls[0].find_element(By.XPATH, remove_adults_xpath)
                    add_adult_button = room_controls[0].find_element(By.XPATH, increase_adults_xpath)

                    if current_adults < adults:
                        add_adult_button.click()
                        # self.move_and_click(add_adult_button)
                        self.random_wait()
                    else:
                        remove_adult_button.click()
                        # self.move_and_click(remove_adult_button)
                        self.random_wait()

                    adults_input = self.wait.until(EC.presence_of_element_located((By.XPATH, adults_input_xpath)))
                    current_adults = int(adults_input.get_attribute("value"))

                # some_shit = self.driver.find_elements(By.XPATH, f"//*[contains(@class, 'uitk-layout-flex uitk-layout-flex-item uitk-step-input-controls')]")
                # add_adult_button = some_shit[0].find_elements(By.XPATH, f".//button")[1]

                # # for each adults
                # for i in range(adults - 1):
                #     if add_adult_button.is_enabled():
                #         print(f"add adult {i}")
                #         self.wait.until(EC.element_to_be_clickable((By.XPATH, increase_adults_xpath)))
                #         add_adult_button.click()
                #         print(f"adults clicked")
                #         self.random_wait()

            if children and children > 0:

                increase_children_xpath = f".//button[contains(@class,'steppers-icon-right')]"
                # # add adult
                # add_adult_button = self.driver.find_element(By.XPATH, f"//*[@aria-describedby='adultCountLabel']")
                # add_adult_button.click()

                for i in range(children):
                    add_children_button = room_controls[1].find_element(By.XPATH, increase_children_xpath)
                    if add_children_button.is_enabled():
                        print(f"add children {i}")
                        add_children_button.click()
                        # self.move_and_click(add_children_button)
                        self.random_wait()

                children_ages_xpath = f"//div[@class='stepper__distribution_container']//select[contains(@class,'select')]"
                children_ages = self.driver.find_elements(By.XPATH, children_ages_xpath)

                for i in range(children_ages.__len__()):
                    self.random_wait()
                    Select(children_ages[i]).select_by_value("10")

            guest_done_button_xpath = f".//*[contains(@class, '-primary') or contains(text(), 'Aplicar')]"
            try:
                done_button = room_controls_footer.find_element(By.XPATH, guest_done_button_xpath)
                self.random_wait()
            except:
                print(f'Element not found or webpage not loaded in time: {guest_done_button_xpath}')
                self.save_screenshot()
                raise Exception(f'Element not found or webpage not loaded in time: {guest_done_button_xpath}')

            done_button.click()
            # self.move_and_click(done_button)

            self.random_wait()
            self.random_wait()

        rooms_part()

        search_button_xpath = f"//*[contains(@class, 'sbox5-box-content')]//*[contains(text(),'Buscar') or contains(text(), 'Search')]"

        try:
            search_button = self.wait.until(EC.presence_of_element_located((By.XPATH, search_button_xpath)))
            self.random_wait()
        except:
            print(f'Element not found or webpage not loaded in time: {search_button_xpath}')
            self.save_screenshot()
            raise Exception(f'Element not found or webpage not loaded in time: {search_button_xpath}')

        # # Disable JavaScript execution
        # self.driver.execute_cdp_cmd("Runtime.disable", {})

        search_button.click()
        # self.move_and_click(search_button)

        self.random_wait()

        # # Enable JavaScript execution
        # self.driver.execute_cdp_cmd("Runtime.enable", {})

        # self.driver.execute_script(f"window.open('_blank', 'Testing');")
        # self.driver.switch_to.window(self.driver.window_handles[1])
        # self.random_wait()
        # self.driver.switch_to.window(self.driver.window_handles[0])

        # modal_xpath = f"//*[contains(@class, 'login-aggressive--content')]"
        #
        # try:
        #     modal = self.wait.until(EC.presence_of_element_located((By.XPATH, modal_xpath)))
        #     # Calculate a point outside the modal
        #     outside_point = modal.location['x'] + modal.size['width'] + 100, modal.location['y']
        #
        #     # Move to that point and click
        #     ActionChains(self.driver).move_to_element_with_offset(modal, outside_point[0],
        #                                                      outside_point[1]).click().perform()
        # except:
        #     print(f'Element not found or webpage not loaded in time: {modal_xpath}')
        #     print(f'No modal found, continue')

        close_stay_usa_xpath = f"//*[contains(text(), 'Continuar no Decolar Brasil')]"
        try:
            self.random_wait()
            close_modal = self.wait.until(EC.presence_of_element_located((By.XPATH, close_stay_usa_xpath)))
            self.random_wait()
            close_modal.click()
            # self.move_and_click(close_modal)
            self.random_wait()
        except:
            print(f'Element not found or webpage not loaded in time: {close_stay_usa_xpath}')

        close_modal_xpath = f"//*[contains(@class, 'login-aggressive--button login-aggressive--button-close shifu-3-btn-ghost')]"
        try:
            self.random_wait()
            close_modal = self.wait.until(EC.presence_of_element_located((By.XPATH, close_modal_xpath)))
            self.random_wait()
            close_modal.click()
            self.move_and_click(close_modal)
            self.random_wait()
        except:
            print(f'Element not found or webpage not loaded in time: {close_modal_xpath}')

        select_currency_xpath = f"//select[option[@value='USD'] or option[@value='BRL']]"
        try:
            self.random_wait()
            select_currency = Select(self.wait.until(EC.presence_of_element_located((By.XPATH, select_currency_xpath))))
            select_currency.select_by_value('USD')
            self.random_wait()
        except:
            print(f'Element not found or webpage not loaded in time: {select_currency_xpath}')
            self.save_screenshot()
            raise Exception(f'Element not found or webpage not loaded in time: {select_currency_xpath}')

        try:
            # Wait for the div with the `infinitescroll` attribute to not have the `-eva-3-hide` class
            self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@infinitescroll and  not(contains(@class, '-eva-3-hide'))]"))
            )
        except Exception:
            print('Timed out waiting for the div with "infinitescroll" attribute to become visible.')
            self.save_screenshot()

        property_listing_result_xpath = f"//*[contains(@class,'results-cluster-container') and not(contains(@class,'results-banner-inner'))]"

        try:
            # Wait up to 10 seconds before throwing a TimeoutException unless it finds the element to return within 10 seconds
            results_property = self.wait.until(
                EC.presence_of_all_elements_located((By.XPATH, property_listing_result_xpath))
            )
        except:
            print(f'Element not found or webpage not loaded in time: {property_listing_result_xpath}')
            self.save_screenshot()
            raise Exception(f'Element not found or webpage not loaded in time: {property_listing_result_xpath}')

        self.random_wait()

        negative_theme_class = 'uitk-text-negative-theme'  # sin disponibilidad / we are sold out
        property_class = 'uitk-spacing uitk-spacing-margin-blockstart-three'
        # results_property = self.driver.find_element(By.XPATH,
        #                                             f"//*[@data-stid='{property_listing_result_stid}']") \
        #                               .find_elements(By.XPATH,
        #                                              f".//div[@class='{property_class}']")

        # data-test-id="price-summary" # we can look for this.

        # pyautogui.hotkey("Ctrl", "Shift", "J")  # close dev tab tool

        found = False
        for i in range(results_property.__len__()):
            result_element = results_property[i]

            # print(f"title_element_text: {title_element.text}")
            found_elements = location.lower() in result_element.text.lower()

            if found_elements:
                print(f"found location: {location} in {result_element.text}")

                try:
                    sold_out = result_element.find_element(By.XPATH,
                                                           f".//*[@class='{negative_theme_class}']")

                    if sold_out:
                        print(f"Sold out")
                        continue
                        # yield item

                except NoSuchElementException:
                    print("Not sold out.")

                if result_element.is_enabled():
                    print(f"click room {i}")

                    # Now, you can clear the request history
                    del self.driver.requests

                    result_element.location_once_scrolled_into_view
                    self.save_screenshot()

                    self.driver.implicitly_wait(10)

                    result_element.click()
                    # self.move_and_click(result_element)
                    # ActionChains(self.driver).move_to_element(result_element).click(result_element).perform()

                    # self.wait.until(EC.number_of_windows_to_be(2))
                    #
                    # # Switch to the new tab. It's usually the last tab in the window_handles list.
                    # self.driver.switch_to.window(self.driver.window_handles[-1])

                    # Store the original window handle for reference
                    original_window_handle = self.driver.current_window_handle

                    # Wait for a new window or tab to be opened
                    self.wait.until(EC.new_window_is_opened([original_window_handle]))

                    # Switch to the new window or tab, which should be the last in the list of window handles
                    new_window_handle = [handle for handle in self.driver.window_handles if handle != original_window_handle][0]
                    self.driver.switch_to.window(new_window_handle)

                    found = True
                    break

        if not found:
            print(f"not found {location}")
            self.save_screenshot()
            raise Exception(f"not found {location}")

        self.driver.implicitly_wait(10)

        section_room_xpath = f"//*[contains(@class, 'rooms-container')]"
        try:
            # Wait up to 10 seconds before throwing a TimeoutException unless it finds the element to return within 10 seconds
            self.wait.until(EC.presence_of_element_located((By.XPATH, section_room_xpath)))
            self.random_wait()
        except:
            print(f'Element not found or webpage not loaded in time: {section_room_xpath}')
            self.save_screenshot()
            raise Exception(f'Element not found or webpage not loaded in time: {section_room_xpath}')

        # Get the json result using the proxy solution found

        filtered_requests = []
        for request in self.driver.requests:
            if '/s-accommodations/api/accommodations/availability/rooms' in request.path \
                    and request.response.body:
                filtered_requests.append(request)

        print(f"requests found: {filtered_requests.__len__()} out of {self.driver.requests.__len__()}")

        data_found = False
        if filtered_requests.__len__() == 1:
            request = filtered_requests[0]

            response_body = self.decode_body(request.response)

            # Parse the request body as JSON
            body = json.loads(response_body)

            # if body is a list get the first element
            if isinstance(body, list):
                body = body[0]

            response = self.standardize_data(body)

            data_found = True
            logger.debug(f"Request URL: {request.url} \nResponse status:{request.response.status_code}")

        if not data_found:
            self.save_screenshot()
            raise Exception(f"Data not found")

        self.exit_driver()

        return response

    def standardize_data(self, data):
        return get_standard_data_second(data, self.params)


