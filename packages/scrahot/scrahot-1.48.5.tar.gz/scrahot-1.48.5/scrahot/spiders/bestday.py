import calendar
import datetime
import json
import random
import re
import time

from loguru import logger
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


class BestdaySeleniumBase(BaseSelenium):
    def __init__(self):
        super().__init__('sb')

        self.name = 'bestday'

        self.params = {}

        self.requests_handle = XHRListener()

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
                              # uc_cdp_events=True,  # Enable CDP Mode for advanced evasion
                            headed=True,              # Use headful mode
                            xvfb=True,                # Use virtual display for Docker
                            # use_auto_ext=False,       # Disable automation extensions
                            # disable_csp=True,         # Disable Content Security Policy
                            # incognito=True,           # Use incognito mode
                              # chromium_arg="--disable-blink-features=AutomationControlled",
                              maximize=True, timeout_multiplier=3, save_screenshot=True,) as sb):
            try:
                url = 'https://www.bestday.com.mx/hoteles/'
                # url = 'https://google.com/ncr'
                sb.activate_cdp_mode(url)
                sb.sleep(2.5)

                # self.save_screenshot("google", driver=sb)
                # try:
                #     sb.cdp.type('[title="Search"]', "bestday.com")
                #     sb.cdp.click('[value*="Google Search"]')
                # except Exception as e:
                #     sb.cdp.type('[title="Buscar"]', "bestday.com")
                #     sb.cdp.click('[value*="Buscar co Ritmon Google"]')
                # sb.sleep(1)
                #
                # self.save_screenshot("google_search", driver=sb)
                #
                # try:
                #     sb.cdp.click('g-raised-button[jsaction*="click"]')
                #     sb.sleep(1)
                # except Exception as e:
                #     logger.info(f"g-raised-button not found or couldn't be clicked: {str(e)}")
                #
                # # navigator_webdriver = sb.execute_script("return navigator.webdriver")
                # # logger.info(f"navigator_webdriver: {navigator_webdriver}")
                #
                # sb.cdp.click('[href*="www.bestday.com"]')
                # sb.sleep(10.5)
                #
                # self.save_screenshot("home", driver=sb)
                #
                # sb.cdp.click('[href*="/hoteles"]')

                self.close_login_incentive(sb)

                self.save_screenshot("home", driver=sb)

                def location_part():
                    # Enter Location
                    # location  _btn
                    location_selector = "input[placeholder*='Ingresa una ciudad']"
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

                    # sb.cdp.mouse_click(".sbox5-title-closed-packages")
                    # sb.sleep(.2)

                    # sb.cdp.click(location_selector)
                    # sb.sleep(1)

                    suggestion = sb.cdp.find_element(
                        "div.ac-wrapper.-show div.ac-container li",
                        timeout=30
                    )
                    suggestion.mouse_click()
                    sb.sleep(1)

                location_part()

                def calendar_part():

                    self.close_login_incentive(sb)

                    # Enter Dates
                    # date_field
                    sb.cdp.click("input[placeholder*='Entrada']")
                    sb.sleep(1)

                    prev_btn = sb.cdp.find_element("a.calendar-arrow-left")
                    next_btn = sb.cdp.find_element("a.calendar-arrow-right")

                    month_left_xpath = f"[@class='uitk-month uitk-month-double uitk-month-double-left']"
                    month_right_xpath = f"[@class='uitk-month uitk-month-double uitk-month-double-right']"
                    month_left, month_right = self.get_months_container(sb)

                    month_label_class = 'sbox5-monthgrid-title'
                    month_label_selector = f".{month_label_class.replace(' ', '.')}"
                    month_label = month_left.query_selector(month_label_selector)
                    spanish_to_english = {
                        'enero': 'January', 'febrero': 'February', 'marzo': 'March',
                        'abril': 'April', 'mayo': 'May', 'junio': 'June',
                        'julio': 'July', 'agosto': 'August', 'septiembre': 'September',
                        'octubre': 'October', 'noviembre': 'November', 'diciembre': 'December'
                    }

                    month_name = month_label.text.split()[0].lower()
                    current_month = spanish_to_english.get(month_name, month_name)
                    current_year = int(month_label.text.split()[-1])
                    target_month = start_date.strftime("%B").lower()
                    target_year = start_date.year

                    while (current_month.lower() != target_month or current_year != target_year):
                        if (current_year < target_year) or (current_year == target_year and
                                                            datetime.datetime.strptime(current_month,
                                                                                       "%B").month < start_date.month):
                            next_btn.click()
                        else:
                            prev_btn.click()
                        sb.sleep(1)
                        month_left, month_right = self.get_months_container(sb)
                        month_label = month_left.query_selector(month_label_selector)
                        month_name = month_label.text.split()[0].lower()
                        current_month = spanish_to_english.get(month_name, month_name)
                        current_year = int(month_label.text.split()[-1])

                    # Select dates
                    day_filter = ('(contains(@class, "uitk-date-number") '
                                  'or contains(@class, "uitk-date-picker-day-number") '
                                  'or contains(@class, "uitk-date-picker-day") '
                                  'or contains(@class, "uitk-day"))')

                    month_left, month_right = self.get_months_container(sb)
                    start_day_btn = sb.cdp.find_element(
                        f".//*[contains(@class, 'sbox5-monthgrid-datenumber-number') and text()='{start_day}']"
                    )

                    start_day_btn.click()
                    sb.sleep(1)

                    month_left, month_right = self.get_months_container(sb)
                    if end_date.month == start_date.month and end_date.year == start_year:
                        end_day_btn = sb.cdp.find_element(
                            f".//*[contains(@class, 'sbox5-monthgrid-datenumber-number') and text()='{end_day}']"
                        )
                    else:
                        end_day_btn = sb.cdp.find_element(
                            f".//*[contains(@class, 'sbox5-monthgrid-datenumber-number') and text()='{end_day}']")
                    end_day_btn.click()
                    sb.sleep(1)

                    # dont_btn
                    sb.cdp.click(".calendar-footer button:nth-child(2)")
                    sb.sleep(1)

                calendar_part()

                self.close_login_incentive(sb)

                def rooms_part():
                    # Enter Guests
                    # guest_field
                    guest_field = sb.cdp.click(f".sbox5-3-first-input-wrapper, .sbox5-3-second-input-wrapper")
                    sb.sleep(1)

                    room_controls_selector = "div.stepper__distribution_container .stepper__room__row"
                    room_controls = sb.cdp.select_all(room_controls_selector)

                    adults_input = room_controls[0].query_selector("input.steppers-tag")
                    current_adults = int(adults_input.get_attribute("value"))

                    remove_btn = room_controls[0].query_selector("button.steppers-icon-left")
                    add_btn = room_controls[0].query_selector("button.steppers-icon-right")

                    while current_adults != adults:
                        if current_adults < adults:
                            add_btn.click()
                        else:
                            remove_btn.click()
                        sb.sleep(1)
                        adults_input = room_controls[0].query_selector(
                         'input[id*="adult-input-0"], input[id*="traveler_selector_adult_step_input-0"]')
                        current_adults = int(adults_input.get_attribute("value"))

                    if children > 0:
                        add_child_btn = room_controls[1].query_selector('button.uitk-step-input-touch-target:nth-of-type(2)')
                        for _ in range(children):
                            add_child_btn.click()
                            sb.sleep(1)

                        # age_selects = sb.cdp.find_element(
                        #     '//select[contains(@class,"age-traveler_selector_children_age_selector") or contains(@name,"child-traveler_selector_children_age_selector")]')

                        age_selects = sb.cdp.find_element('select.age-traveler_selector_children_age_selector, select[name*="child-traveler_selector_children_age_selector"]')

                        for select in age_selects:
                            sb.cdp.select_option_by_text(select, "10")
                            sb.sleep(0.5)

                    # guest_done
                    # sb.cdp.click('//*[contains(@id,"traveler_selector_done_button") or contains(@data-testid, "guests-done-button")]')
                    sb.cdp.click('#traveler_selector_done_button, [data-testid="guests-done-button"]')
                    sb.sleep(1)

                # rooms_part()

                # Search
                # search_btn
                sb.cdp.click(".sbox5-box-content [id*='search-button'], .sbox5-box-content button:contains('Buscar'), .sbox5-box-content button:contains('Search')")
                sb.sleep(3)

                try:
                    close_modal = sb.cdp.find_element('.login-aggressive--button.login-aggressive--button-close')
                    close_modal.click()
                    sb.sleep(0.5)
                except Exception as e:
                    logger.debug(f"Login aggressive modal not found or couldn't be closed: {str(e)}")

                self.select_currency_process(sb)
                sb.cdp.wait_for_element_visible(".results-cluster-container:not(.results-banner-inner)", timeout=30)
                for i in range(10):
                    sb.cdp.scroll_down(8)

                # Find hotel
                hotel_cards = sb.cdp.select_all(".results-cluster-container:not(.results-banner-inner)", timeout=30)

                found = False
                for card in hotel_cards:
                    if location.lower() in card.text.lower():
                        card.scroll_into_view()
                        card.mouse_click()
                        sb.sleep(2)
                        found = True
                        break

                if not found:
                    raise Exception(f"Hotel not found for location: {location}")

                while len(sb.cdp.get_tabs()) > 1:
                    sb.cdp.close_active_tab()
                    sb.cdp.switch_to_newest_tab()
                    sb.sleep(0.6)

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

                rooms = []
                all_rooms = sb.cdp.select_all('[class="rooms-container"] > aloha-roompacks-group-container')
                for room in all_rooms:
                    # room = all_rooms.query_selector(f'{room_child.attrs.class_.replace(" ", ".")}')
                    room.scroll_into_view()

                    sb.sleep(0.5)

                    # price_element = room.query_selector('[class="eva-3-p -eva-3-tc-gray-0 -eva-3-mt-sm additional-caption-message focused-message"]') # per night
                    price_element = room.query_selector('[class="main-value"]') # total nights
                    if not price_element:
                        logger.debug(f"No price found for room {room}")
                        continue
                    price = re.sub(r'[^\d.,]', '', price_element.text).replace('.', '').replace(',', '.')

                    name = room.query_selector('[class*="room-name"]').text.strip()
                    beds = room.query_selector('[class="eva-3-caption bed-options-text"]').text.strip()

                    room = {
                        "name": name,
                        "beds": beds,
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
                response['success'] = False
                response['error'] = f"{type(e).__name__}: {str(e)}"
                logger.debug(f"Error: {type(e).__name__}: {e}")

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
            sb.cdp.click("[class*='login-incentive--button-close']", timeout=30)
        except Exception as e:
            logger.debug(f"Login incentive not found or couldn't be closed: {str(e)}")

    def select_currency_process(self, sb):
        # currency_btn
        """Select USD currency."""
        sb.cdp.select_option_by_text("select:has(option[value='USD'], option[value='MXN'])", "Dólar")
        sb.sleep(2)

    def get_months_container(self, sb):
        calendar_container_path = ".calendar-container div.sbox5-monthgrid"
        calendar_container = sb.cdp.find_elements(calendar_container_path)

        month_left = calendar_container[0]
        month_right = calendar_container[1]

        return month_left, month_right

    def standardize_data(self, data):
        return get_standard_data_second(data, self.params)



# class BestdaySelenium(BaseSelenium):
#
#     def __init__(self):
#         super().__init__()
#
#         self.name = 'bestday'
#
#         # Only request URLs containing "bestday" or "whatever" will now be captured
#         self.driver.scopes = [
#             '.*bestday.*',
#         ]
#
#         self.params = {}
#
#     def get_rooms(self, params):
#         logger.debug(f'get_rooms: {params}')
#         self.params = params
#
#         website, region, location, start_day, start_month, start_year, end_day, end_month, end_year, adults, children, start_date, end_date = self.validate_input_data()
#
#         url = 'https://bestday.com.mx/hoteles'
#         self.driver.get(url)
#
#         logger.debug(f'url: {url}')
#
#         self.driver.implicitly_wait(10)
#
#         def close_login_incentive():
#             # close the login incentive
#             close_login_incentive_xpath = f"//div[contains(@class, 'login-incentive--button-close')]"
#             try:
#                 close_login_incentive = self.wait.until(EC.presence_of_element_located((By.XPATH, close_login_incentive_xpath)))
#                 close_login_incentive.location_once_scrolled_into_view
#                 close_login_incentive.click()
#             except:
#                 print(f'Element not found or webpage not loaded in time: {close_login_incentive_xpath}')
#
#         close_login_incentive()
#
#         # *** Entering LOCATION ***
#         def location_part():
#
#             destination_form_field_xpath = f"//input[contains(@placeholder, 'Ingresa una ciudad')]"
#             try:
#                 print(f'waiting for: {destination_form_field_xpath}')
#                 # Wait for actions to complete
#                 input_element = self.wait.until(EC.presence_of_element_located((By.XPATH, destination_form_field_xpath)))
#             except:
#                 print(f'Element not found or webpage not loaded in time: {destination_form_field_xpath}')
#                 self.save_screenshot()
#                 raise Exception(f'Element not found or webpage not loaded in time: {destination_form_field_xpath}')
#
#             print(f'entering keys for: {destination_form_field_xpath}')
#
#             print(f'waiting to be clickable: {destination_form_field_xpath}')
#             # Use JavaScript to change the autocomplete attribute to 'on'
#
#             print(f'input_element: {input_element.text}')
#             # Send keys to the input element
#             input_element.click()
#             # self.move_and_click(input_element)
#             self.random_wait()
#             input_element.send_keys(location)
#
#             self.random_wait()
#
#             input_element_selection_xpath = f"//*[contains(@class, 'ac-wrapper') and contains(@class, '-show')]//*[contains(@class, 'ac-container')]//li"
#             try:
#                 input_element_selection = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, input_element_selection_xpath)))
#             except:
#                 print(f'Element not found or webpage not loaded in time: {input_element_selection_xpath}')
#                 self.save_screenshot()
#                 raise Exception(f'Element not found or webpage not loaded in time: {input_element_selection_xpath}')
#             input_element_selection[0].click()
#             # self.move_and_click(input_element_selection[0])
#
#             self.random_wait()
#
#             input_element.send_keys(Keys.ENTER)
#
#             # Simulate typing some words
#             # self.driver.switch_to.active_element.send_keys(location)
#             # # Simulate hitting the Enter key
#             # self.driver.switch_to.active_element.send_keys(Keys.ENTER)
#
#             self.random_wait()
#
#         location_part()
#
#         # *** Entering DATE ***
#         def calendar_part():
#             date_button_data_xpath = f"//*[contains(@placeholder, 'Entrada')]"
#             print(f'preparing for: {date_button_data_xpath}')
#
#             # Find the button using its data-stid attribute and click it
#             date_button = self.driver.find_element(By.XPATH, date_button_data_xpath)
#             date_button.click()
#             # self.move_and_click(date_button)
#
#             self.random_wait()
#
#             prev_button_month = self.driver.find_element(By.XPATH,
#                                                          f"//a[contains(@class, 'calendar-arrow-left')]")
#             next_button_month = self.driver.find_element(By.XPATH,
#                                                          f"//a[contains(@class, 'calendar-arrow-right')]")
#
#             calendar_container_path = f"//*[contains(@class,'calendar-container')]/div[contains(@class, 'sbox5-monthgrid')]"
#             month_left = self.driver.find_elements(By.XPATH, calendar_container_path)[0]
#             month_right = self.driver.find_elements(By.XPATH, calendar_container_path)[1]
#
#             month_label_class = 'sbox5-monthgrid-title'
#             month_left_label = month_left.find_element(By.XPATH, f".//*[contains(@class, '{month_label_class}')]")
#             start_date_text = month_left_label.text
#             cal_start_month_name = start_date_text.split()[0]
#             spanish_to_english = {
#                 'enero': 'January',
#                 'febrero': 'February',
#                 'marzo': 'March',
#                 'abril': 'April',
#                 'mayo': 'May',
#                 'junio': 'June',
#                 'julio': 'July',
#                 'agosto': 'August',
#                 'septiembre': 'September',
#                 'octubre': 'October',
#                 'noviembre': 'November',
#                 'diciembre': 'December'
#             }
#             cal_start_month_name = spanish_to_english.get(cal_start_month_name.lower(), cal_start_month_name.lower()).lower()
#             # Convert month name to month number using datetime module
#             cal_start_month_number = datetime.datetime.strptime(cal_start_month_name, "%B").month
#             year = int(start_date_text.split()[-1])
#
#             # iterate to the correct month
#             while not (start_year == year and start_date.month == cal_start_month_number):
#                 # iterate to the next month or previous month
#                 if start_year < year and start_date.month < cal_start_month_number:
#                     prev_button_month.click()
#                     # self.move_and_click(prev_button_month)
#                 elif start_year > year or start_date.month > cal_start_month_number:
#                     next_button_month.click()
#                     # self.move_and_click(next_button_month)
#
#                 self.random_wait()
#
#                 month_left = self.driver.find_elements(By.XPATH, calendar_container_path)[0]
#                 month_right = self.driver.find_elements(By.XPATH, calendar_container_path)[1]
#
#                 try:
#                     month_left_label = month_left.find_element(By.XPATH, f".//*[contains(@class, '{month_label_class}')]")
#                 except:
#                     print(f'Element not found or webpage not loaded in time: {month_label_class}')
#                     self.save_screenshot()
#                     raise Exception(f'Element not found or webpage not loaded in time: {month_label_class}')
#
#                 start_date_text = month_left_label.text
#
#                 cal_start_month_name = start_date_text.split()[0]
#                 cal_start_month_name = spanish_to_english.get(cal_start_month_name.lower(),
#                                                               cal_start_month_name.lower()).lower()
#                 cal_start_month_number = datetime.datetime.strptime(cal_start_month_name, "%B").month
#                 year = int(start_date_text.split()[-1])
#
#             # setting start date
#             if start_date.month == cal_start_month_number and start_year == year:
#                 # select the start day
#                 # month_left.find_element(By.XPATH, f"//*[text()='{start_day}']").click()
#
#                 day_button = month_left.find_element(By.XPATH,
#                                                      f".//*[contains(@class, 'sbox5-monthgrid-datenumber-number') and text()='{start_day}']")
#
#                 day_button.location_once_scrolled_into_view
#                 day_button.click()
#                 # self.move_and_click(day_button)
#                 self.random_wait()
#
#             # setting end date
#
#             month_left = self.driver.find_elements(By.XPATH, calendar_container_path)[0]
#             month_right = self.driver.find_elements(By.XPATH, calendar_container_path)[1]
#
#             # if the end date is in the left month of the calendar
#             if end_month.lower() in cal_start_month_name.lower() and end_year == year:
#                 # select the end day
#                 try:
#                     day_button = month_left.find_element(By.XPATH,
#                                                          f".//*[contains(@class, 'sbox5-monthgrid-datenumber-number') and text()='{end_day}']")
#
#                     day_button.click()
#                     # self.move_and_click(day_button)
#                     self.random_wait()
#                 except:
#                     print(f'Element not found or webpage not loaded in time: {end_day}')
#                     # if this gives error is because the date is already selected.
#
#             else:
#                 try:
#                     # we look in the right calendar month
#                     day_button = month_right.find_elements(By.XPATH,
#                                                            f".//*[contains(@class, 'sbox5-monthgrid-datenumber-number') and text()='{end_day}']")
#
#                     if day_button.__len__() > 1:
#                         day_button[1].click()
#                         # self.move_and_click(day_button[1])
#                     else:
#                         day_button[0].click()
#                         # self.move_and_click(day_button[0])
#                     self.random_wait()
#                 except:
#                     print(f'Element not found or webpage not loaded in time: {end_day}')
#                     # if this gives error is because the date is already selected.
#
#             calendar_done_button_xpath = f"//*[contains(@class, 'calendar-footer')]//button"
#             try:
#                 calendar_done_button = self.driver.find_element(By.XPATH, calendar_done_button_xpath)
#             except:
#                 print(f'Element not found or webpage not loaded in time: {calendar_done_button_xpath}')
#                 self.save_screenshot()
#                 raise Exception(f'Element not found or webpage not loaded in time: {calendar_done_button_xpath}')
#             calendar_done_button.click()
#             # self.move_and_click(calendar_done_button)
#             self.random_wait()
#
#         calendar_part()
#
#         close_login_incentive()
#
#         # *** Entering GUESTS ***
#         def rooms_part():
#             room_picker_data_xpath = f"//*[contains(@class, 'sbox5-3-first-input-wrapper') or contains(@class, 'sbox5-3-second-input-wrapper')]"
#             try:
#                 button_room_picker = self.wait.until(EC.presence_of_element_located((By.XPATH, room_picker_data_xpath)))
#             except:
#                 print(f'Element not found or webpage not loaded in time: {room_picker_data_xpath}')
#                 self.save_screenshot()
#                 raise Exception(f'Element not found or webpage not loaded in time: {room_picker_data_xpath}')
#
#             button_room_picker.click()
#             # self.move_and_click(button_room_picker)
#
#             self.random_wait()
#
#             room_controls_xpath = f"//div[@class='stepper__distribution_container']//*[@class='stepper__room__row']"
#             room_controls = self.driver.find_elements(By.XPATH, room_controls_xpath)
#
#             room_controls_footer_xpath = f"//div[contains(@class, 'distribution__container')]//*[contains(@class,'stepper__room__footer')]"
#             room_controls_footer = self.driver.find_element(By.XPATH, room_controls_footer_xpath)
#
#             # remove_adults_xpath = f".//descendant::button[1]"
#             adults_input_xpath = f".//input[contains(@class, 'steppers-tag')]"

#             adults_input = room_controls[0].find_elements(By.XPATH, adults_input_xpath)[0]
#
#             # increase_adults_xpath = f".//descendant::button[2]"
#             remove_adults_xpath = f".//button[contains(@class,'steppers-icon-left')]"
#             increase_adults_xpath = f".//button[contains(@class,'steppers-icon-right')]"
#             if adults and adults >= 1:
#                 current_adults = int(adults_input.get_attribute("value"))
#                 while current_adults != adults:
#                     remove_adult_button = room_controls[0].find_element(By.XPATH, remove_adults_xpath)
#                     add_adult_button = room_controls[0].find_element(By.XPATH, increase_adults_xpath)
#
#                     if current_adults < adults:
#                         add_adult_button.click()
#                         # self.move_and_click(add_adult_button)
#                     else:
#                         remove_adult_button.click()
#                         # self.move_and_click(remove_adult_button)
#
#                     self.random_wait()
#
#                     adults_input = self.wait.until(EC.presence_of_element_located((By.XPATH, adults_input_xpath)))
#                     current_adults = int(adults_input.get_attribute("value"))
#
#                 # some_shit = self.driver.find_elements(By.XPATH, f"//*[contains(@class, 'uitk-layout-flex uitk-layout-flex-item uitk-step-input-controls')]")
#                 # add_adult_button = some_shit[0].find_elements(By.XPATH, f".//button")[1]
#
#                 # # for each adults
#                 # for i in range(adults - 1):
#                 #     if add_adult_button.is_enabled():
#                 #         print(f"add adult {i}")
#                 #         self.wait.until(EC.element_to_be_clickable((By.XPATH, increase_adults_xpath)))
#                 #         add_adult_button.click()
#                 #         print(f"adults clicked")
#                 #         self.random_wait()
#
#             if children and children > 0:
#
#                 increase_children_xpath = f".//button[contains(@class,'steppers-icon-right')]"
#                 # # add adult
#                 # add_adult_button = self.driver.find_element(By.XPATH, f"//*[@aria-describedby='adultCountLabel']")
#                 # add_adult_button.click()
#
#                 for i in range(children):
#                     add_children_button = room_controls[1].find_element(By.XPATH, increase_children_xpath)
#                     if add_children_button.is_enabled():
#                         print(f"add children {i}")
#                         add_children_button.click()
#                         # self.move_and_click(add_children_button)
#                         self.random_wait()
#
#                 children_ages_xpath = f"//div[@class='stepper__distribution_container']//select[contains(@class,'select')]"
#                 children_ages = self.driver.find_elements(By.XPATH, children_ages_xpath)
#
#                 for i in range(children_ages.__len__()):
#                     Select(children_ages[i]).select_by_value("10")
#
#             guest_done_button_xpath = f".//*[contains(@class, '-primary') or contains(text(), 'Aplicar')]"
#             try:
#                 done_button = room_controls_footer.find_element(By.XPATH, guest_done_button_xpath)
#             except:
#                 print(f'Element not found or webpage not loaded in time: {guest_done_button_xpath}')
#                 self.save_screenshot()
#                 raise Exception(f'Element not found or webpage not loaded in time: {guest_done_button_xpath}')
#
#             done_button.click()
#             # self.move_and_click(done_button)
#
#             self.random_wait()
#
#         rooms_part()
#
#         search_button_xpath = f"//*[contains(@class, 'sbox5-box-content')]//*[contains(text(),'Buscar') or contains(text(), 'Search')]"
#
#         try:
#             search_button = self.wait.until(EC.presence_of_element_located((By.XPATH, search_button_xpath)))
#         except:
#             print(f'Element not found or webpage not loaded in time: {search_button_xpath}')
#             self.save_screenshot()
#             raise Exception(f'Element not found or webpage not loaded in time: {search_button_xpath}')
#
#         search_button.click()
#         # self.move_and_click(search_button)
#
#         self.random_wait()
#
#         # modal_xpath = f"//*[contains(@class, 'login-aggressive--content')]"
#         #
#         # try:
#         #     modal = self.wait.until(EC.presence_of_element_located((By.XPATH, modal_xpath)))
#         #     # Calculate a point outside the modal
#         #     outside_point = modal.location['x'] + modal.size['width'] + 100, modal.location['y']
#         #
#         #     # Move to that point and click
#         #     ActionChains(self.driver).move_to_element_with_offset(modal, outside_point[0],
#         #                                                      outside_point[1]).click().perform()
#         # except:
#         #     print(f'Element not found or webpage not loaded in time: {modal_xpath}')
#         #     print(f'No modal found, continue')
#
#         close_modal_xpath = f"//*[contains(@class, 'login-aggressive--button login-aggressive--button-close shifu-3-btn-ghost')]"
#         try:
#             close_modal = self.wait.until(EC.presence_of_element_located((By.XPATH, close_modal_xpath)))
#             close_modal.click()
#             # self.move_and_click(close_modal)
#         except:
#             print(f'Element not found or webpage not loaded in time: {close_modal_xpath}')
#
#         select_currency_xpath = f"//select[.//option[@value='USD'] or .//option[@value='MXN']]"
#         try:
#             self.random_wait()
#             select_currency = Select(self.wait.until(EC.presence_of_element_located((By.XPATH, select_currency_xpath))))
#             select_currency.select_by_value('USD')
#             self.random_wait()
#             self.random_wait()
#             self.random_wait()
#         except:
#             print(f'Element not found or webpage not loaded in time: {select_currency_xpath}')
#             self.save_screenshot()
#             raise Exception(f'Element not found or webpage not loaded in time: {select_currency_xpath}')
#
#         # get the first hotel in the listing result
#
#         try:
#             # Wait for the div with the `infinitescroll` attribute to not have the `-eva-3-hide` class
#             self.wait.until(
#                 EC.presence_of_element_located(
#                     (By.XPATH, "//div[@infinitescroll and  not(contains(@class, '-eva-3-hide'))]"))
#             )
#         except Exception:
#             print('Timed out waiting for the div with "infinitescroll" attribute to become visible.')
#             self.save_screenshot()
#
#         property_listing_result_xpath = f"//*[contains(@class,'results-cluster-container') and not(contains(@class,'results-banner-inner'))]"
#
#         try:
#             # Wait up to 10 seconds before throwing a TimeoutException unless it finds the element to return within 10 seconds
#             results_property = self.wait.until(
#                 EC.presence_of_all_elements_located((By.XPATH, property_listing_result_xpath))
#             )
#         except:
#             print(f'Element not found or webpage not loaded in time: {property_listing_result_xpath}')
#             # yield item
#             self.save_screenshot()
#             raise Exception(f'Element not found or webpage not loaded in time: {property_listing_result_xpath}')
#
#         self.random_wait()
#
#         negative_theme_class = 'uitk-text-negative-theme'  # sin disponibilidad / we are sold out
#         property_class = 'uitk-spacing uitk-spacing-margin-blockstart-three'
#         # results_property = self.driver.find_element(By.XPATH,
#         #                                             f"//*[@data-stid='{property_listing_result_stid}']") \
#         #                               .find_elements(By.XPATH,
#         #                                              f".//div[@class='{property_class}']")
#
#         # data-test-id="price-summary" # we can look for this.
#
#         found = False
#         for i in range(results_property.__len__()):
#             result_element = results_property[i]
#
#             # print(f"title_element_text: {title_element.text}")
#             found_elements = location.lower() in result_element.text.lower()
#
#             if found_elements:
#                 print(f"found location: {location} in {result_element.text}")
#
#                 try:
#                     sold_out = result_element.find_element(By.XPATH,
#                                                            f".//*[@class='{negative_theme_class}']")
#
#                     if sold_out:
#                         print(f"Sold out")
#                         continue
#                         # yield item
#
#                 except NoSuchElementException:
#                     print("Not sold out.")
#
#                 if result_element.is_enabled():
#                     print(f"click room {i}")
#
#                     # Now, you can clear the request history
#                     del self.driver.requests
#
#                     result_element.location_once_scrolled_into_view
#                     self.save_screenshot()
#                     result_element.click()
#                     # self.move_and_click(result_element)
#                     # ActionChains(self.driver).move_to_element(result_element).click(result_element).perform()
#
#                     # self.wait.until(EC.number_of_windows_to_be(2))
#                     #
#                     # # Switch to the new tab. It's usually the last tab in the window_handles list.
#                     # self.driver.switch_to.window(self.driver.window_handles[-1])
#
#                     # Store the original window handle for reference
#                     original_window_handle = self.driver.current_window_handle
#
#                     # Wait for a new window or tab to be opened
#                     self.wait.until(EC.new_window_is_opened([original_window_handle]))
#
#                     # Switch to the new window or tab, which should be the last in the list of window handles
#                     new_window_handle = \
#                     [handle for handle in self.driver.window_handles if handle != original_window_handle][0]
#                     self.driver.switch_to.window(new_window_handle)
#
#                     found = True
#                     break
#
#         if not found:
#             print(f"not found {location}")
#             self.save_screenshot()
#             raise Exception(f"not found {location}")
#
#         section_room_xpath = f"//*[contains(@class, 'rooms-container')]"
#         try:
#             # Wait up to 10 seconds before throwing a TimeoutException unless it finds the element to return within 10 seconds
#             self.wait.until(EC.presence_of_element_located((By.XPATH, section_room_xpath)))
#         except:
#             print(f'Element not found or webpage not loaded in time: {section_room_xpath}')
#             self.save_screenshot()
#             raise Exception(f'Element not found or webpage not loaded in time: {section_room_xpath}')
#
#         # Get the json result using the proxy solution found
#
#         filtered_requests = []
#         for request in self.driver.requests:
#             if '/s-accommodations/api/accommodations/availability/rooms' in request.path \
#                     and request.response.body:
#                 filtered_requests.append(request)
#
#         print(f"requests found: {filtered_requests.__len__()} out of {self.driver.requests.__len__()}")
#
#         data_found = False
#         if filtered_requests.__len__() == 1:
#             request = filtered_requests[0]
#
#             response_body = self.decode_body(request.response)
#
#             # Parse the request body as JSON
#             body = json.loads(response_body)
#
#             # if body is a list get the first element
#             if isinstance(body, list):
#                 body = body[0]
#
#             response = self.standardize_data(body)
#
#             data_found = True
#             logger.debug(f"Request URL: {request.url} \nResponse status:{request.response.status_code}")
#
#         if not data_found:
#             self.save_screenshot()
#             raise Exception(f"Data not found")
#
#         self.exit_driver()
#
#         return response
#
#     def standardize_data(self, data):
#         return get_standard_data_second(data, self.params)