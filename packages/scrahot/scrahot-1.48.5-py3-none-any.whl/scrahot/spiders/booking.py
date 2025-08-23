import datetime
import json
import re
import time

from loguru import logger
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from seleniumwire.utils import decode

from scrahot.spiders.base import BaseSelenium
from scrahot.standard_json import get_standard_data_booking
from scrahot.utils import XHRListener
import seleniumbase


class BookingSeleniumBase(BaseSelenium):
    def __init__(self):
        super().__init__('sb')

        self.name = 'booking'

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
                            # headed=True,              # Use headful mode
                            # xvfb=True,                # Use virtual display for Docker
                            # use_auto_ext=False,       # Disable automation extensions
                            # disable_csp=True,         # Disable Content Security Policy
                            # incognito=True,           # Use incognito mode
                              # chromium_arg="--disable-blink-features=AutomationControlled",
                              maximize=True, timeout_multiplier=3, save_screenshot=True,) as sb):
            try:
                url = 'https://booking.com/?selected_currency=USD'
                sb.activate_cdp_mode(url)
                sb.sleep(2.5)

                self.save_screenshot("home", driver=sb)

                self.close_login_incentive(sb)

                def location_part():
                    # Enter Location
                    # location  _btn
                    location_selector = "input[placeholder*='Where are you going?']"
                    # sb.cdp.gui_click_element(location_selector)
                    sb.cdp.click(location_selector)
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
                    sb.cdp.press_keys(location_selector, location)
                    sb.sleep(2)
                    # sb.cdp.gui_press_keys(location)
                    # sb.sleep(2)

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

                    suggestion = sb.cdp.find_element(
                        "ul[role*='group'] li",
                        timeout=30
                    )
                    suggestion.mouse_click()
                    sb.sleep(1)

                location_part()

                def calendar_part():

                    self.close_login_incentive(sb)

                    # Enter Dates
                    # date_field
                    # sb.cdp.click("button[data-testid*='searchbox-dates-container']")
                    # sb.sleep(1)

                    # prev_btn = sb.cdp.find_element("button[aria-label*='Previous month']")
                    next_btn = sb.cdp.find_element("button[aria-label*='Next month']")

                    month_left, month_right = self.get_months_container(sb)

                    month_label_selector = f"[aria-live='polite']"
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
                        # else:
                        #     prev_btn.click()
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
                        f"[data-date='{start_date.year}-{start_date.month:02}-{start_date.day:02}']"
                    )

                    start_day_btn.click()
                    sb.sleep(1)

                    # month_left, month_right = self.get_months_container(sb)
                    if end_date.month == start_date.month and end_date.year == start_year:
                        end_day_btn = sb.cdp.find_element(
                            f"[data-date='{end_date.year}-{end_date.month:02}-{end_date.day:02}']"
                        )
                    else:
                        end_day_btn = sb.cdp.find_element(
                            f"[data-date='{end_date.year}-{end_date.month:02}-{end_date.day:02}']"
                        )
                    end_day_btn.click()
                    sb.sleep(1)

                    # dont_btn
                    # sb.cdp.click(".calendar-footer button:nth-child(2)")
                    # sb.sleep(1)

                calendar_part()

                # self.close_login_incentive(sb)

                def rooms_part():
                    # Enter Guests
                    # guest_field
                    room_selector = f"[data-testid='occupancy-config']"
                    sb.cdp.click(room_selector)
                    sb.sleep(1)

                    room_controls_selector = "[data-testid='occupancy-popup'] > div > div"
                    room_controls = sb.cdp.select_all(room_controls_selector)
                    adults_input_selector = "input[id='group_adults']"
                    adults_input = room_controls[0].query_selector(adults_input_selector)
                    current_adults = int(adults_input.get_attribute("value"))

                    remove_btn = room_controls[0].query_selector("button")
                    add_btn = room_controls[0].query_selector_all("button")[1]

                    while current_adults != adults:
                        if current_adults < adults:
                            add_btn.click()
                        else:
                            remove_btn.click()
                        sb.sleep(1)
                        adults_input = room_controls[0].query_selector(adults_input_selector)
                        current_adults = int(adults_input.get_attribute("value"))

                    if children > 0:
                        add_child_btn = room_controls[1].query_selector_all("button")[1]
                        for _ in range(children):
                            add_child_btn.mouse_click()
                            sb.sleep(1)

                        # Find all select elements matching the selector
                        age_selects = sb.find_elements(f"[data-testid='kids-ages-select']")

                        # Iterate over the first, second, and third select elements
                        for index, select in enumerate(age_selects[:3], 1):  # Limit to first three elements
                            # Use SeleniumBase to select option by value for each element
                            # sb.cdp.select_option_by_text(f"[data-testid='kids-ages-select']:nth-child({index}) select[name='age']", "10 years old")
                            sb.select_option_by_value(f"[data-testid='kids-ages-select']:nth-child({index}) select[name='age']", "10")
                            sb.sleep(0.5)  # Pause to ensure the action completes
                            sb.cdp.mouse_click(room_selector)
                            sb.sleep(0.5)

                    # guest_done
                    sb.cdp.click("[data-testid='occupancy-popup'] > button")
                    sb.sleep(1)

                rooms_part()

                # Search
                # search_btn
                sb.cdp.click("button[class*='de576f5064 b46cd7aad7 ced67027e5 dda427e6b5 e4f9ca4b0c ca8e0b9533 cfd71fb584 a9d40b8d51']")
                sb.sleep(3)

                # try:
                #     close_modal = sb.cdp.find_element('.login-aggressive--button.login-aggressive--button-close')
                #     close_modal.click()
                #     sb.sleep(0.5)
                # except Exception as e:
                #     logger.debug(f"Login aggressive modal not found or couldn't be closed: {str(e)}")

                # self.select_currency_process(sb)
                sb.cdp.wait_for_element_visible("[data-testid='property-card']", timeout=30)
                for i in range(10):
                    sb.cdp.scroll_down(8)

                self.close_login_incentive(sb)

                # Find hotel
                hotel_cards = sb.cdp.select_all("[data-testid='property-card']", timeout=30)

                found = False
                for card in hotel_cards:
                    if "This property has no availability on our site".lower() in card.text.lower():
                        return {
                            "success": True,
                            "error": "This property has no avaliability",
                            "search_criteria": params,
                            "hotel": params.get('location'),
                            "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
                        }
                    if location.lower() in card.text.lower():
                        card.scroll_into_view()
                        avail_button = card.query_selector("div[data-testid='title']")
                        avail_button.mouse_click()
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

                rooms_table_selector = "[id='hprt-table'] > tbody > tr"
                sb.cdp.wait_for_element_visible(rooms_table_selector, timeout=30)
                rooms = []
                all_rooms = sb.cdp.select_all(rooms_table_selector)
                block_ids = []
                for room in all_rooms:
                    # room = all_rooms.query_selector(f'{room_child.attrs.class_.replace(" ", ".")}')
                    room.scroll_into_view()

                    sb.sleep(0.5)

                    block_id = room.get_attribute("data-block-id")
                    if block_id in block_ids:
                        logger.info(f"Skipping block {block_id}")
                        continue
                    block_ids.append(block_id)

                    # price_element = room.query_selector('[class="eva-3-p -eva-3-tc-gray-0 -eva-3-mt-sm additional-caption-message focused-message"]') # per night
                    # price_element = room.query_selector('[class="main-value"]') # total nights
                    # if not price_element:
                    #     logger.debug(f"No price found for room {room}")
                    #     continue
                    # price = re.sub(r'[^\d.,]', '', price_element.text).replace('.', '').replace(',', '.')
                    price = room.get_attribute("data-hotel-rounded-price")

                    name = room.query_selector('[data-room-name]')
                    if not name:
                        logger.info(f"Skipping block {block_id}")
                        continue
                    name = name.text.strip()
                    beds = room.query_selector('[class*="bed-types-wrapper"]')

                    if not beds:
                        beds = room.query_selector('[class="rt-bed-type"]')
                    beds = beds.text.strip() if beds else "No beds info"

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
                logger.error(f"Error during Booking Selenium process: {str(e)}")
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
            sb.cdp.click("button[aria-label*='Dismiss sign in info']", timeout=30)
        except Exception as e:
            logger.debug(f"Login incentive not found or couldn't be closed: {str(e)}")

    def select_currency_process(self, sb):
        # currency_btn
        """Select USD currency."""
        sb.cdp.select_option_by_text("select:has(option[value='USD'], option[value='MXN'])", "Dólar")
        sb.sleep(2)

    def get_months_container(self, sb):
        calendar_container_path = "[data-testid='searchbox-datepicker-calendar'] > div > div"
        calendar_container = sb.cdp.find_elements(calendar_container_path)

        month_left = calendar_container[0]
        month_right = calendar_container[1]

        return month_left, month_right

    def standardize_data(self, data):
        return get_standard_data_booking(data, self.params)



class BookingSelenium(BaseSelenium):

    def __init__(self):
        super().__init__()

        self.name = 'booking'

        # Only request URLs containing "booking" or "whatever" will now be captured
        self.driver.scopes = [
            '.*booking.*',
        ]

        self.params = {}

    def get_rooms(self, params):
        logger.debug(f'get_rooms: {params}')
        self.params = params
        website, region, location, start_day, start_month, start_year, end_day, end_month, end_year, adults, children, start_date, end_date = self.validate_input_data()

        url = 'https://booking.com/?selected_currency=USD'
        self.driver.get(url)

        # self.save_screenshot("initial")

        logger.debug(f'url: {url}')

        self.driver.implicitly_wait(10)

        # *** Entering LOCATION ***
        def location_part():
            self.close_sign_up()

            self.random_wait()

            destination_form_field_xpath = f"//input[contains(@class, 'b915b8dc0b')]"
            self.wait_and_click_element(destination_form_field_xpath, raise_exception=False)

            input_element = self.wait_for_element(destination_form_field_xpath)

            # self.save_screenshot("location_part_before1")
            logger.debug(f'entering location: [{location}] for: {destination_form_field_xpath}')
            self.wait.until(EC.element_to_be_clickable((By.XPATH, destination_form_field_xpath)))
            # input_element.send_keys(location)
            input_element.clear()
            for char in location:
                input_element.send_keys(char)
                time.sleep(0.1)  # Adjust delay as needed
            logger.debug(f'location entered: {input_element.text}')

            self.random_wait()
            self.random_wait()
            self.random_wait()

            # self.save_screenshot("location_part_before2")

            input_element_selection_xpath = f"//div[contains(@id, 'autocomplete-results')]//ul//li[1]"
            input_element_selection = self.wait_for_element(input_element_selection_xpath)
            input_element_selection.click()

            # self.save_screenshot("location_part_before3")

            self.random_wait()

            # input_element.send_keys(Keys.ENTER)

            # Simulate typing some words
            # self.driver.switch_to.active_element.send_keys(location)
            # # Simulate hitting the Enter key
            # self.driver.switch_to.active_element.send_keys(Keys.ENTER)

            self.random_wait()

            self.save_screenshot("location_part")

        location_part()

        def date_part():
            # *** Entering DATE ***

            # date_button_data_xpath = f"//*[contains(@data-testid, 'searchbox-dates-container')]"
            # print(f'preparing for: {date_button_data_xpath}')
            #
            # # Find the button using its data-stid attribute and click it
            # date_button = self.driver.find_element(By.XPATH, date_button_data_xpath)
            # date_button.click()

            self.random_wait()

            calendar_container_path = (f"//*[contains(@class,'c92e2bd0cb') "
                                       f"or contains(@data-testid,'searchbox-datepicker-calendar') "
                                       f"or contains(@data-testid,'searchbox-dates-container') "
                                       f"]/div/div ")
            month_left = self.driver.find_elements(By.XPATH, calendar_container_path)[0]
            month_right = self.driver.find_elements(By.XPATH, calendar_container_path)[1]

            month_label_path = f".//*[contains(@class, 'eb73dc0c10 d2fc2d6042') or @aria-live='polite']"
            month_left_label = month_left.find_element(By.XPATH, month_label_path)
            start_date_text = month_left_label.text
            cal_start_month_name = start_date_text.split()[0]
            spanish_to_english = {
                'enero': 'January',
                'febrero': 'February',
                'marzo': 'March',
                'abril': 'April',
                'mayo': 'May',
                'junio': 'June',
                'julio': 'July',
                'agosto': 'August',
                'septiembre': 'September',
                'octubre': 'October',
                'noviembre': 'November',
                'diciembre': 'December'
            }
            cal_start_month_name = spanish_to_english.get(cal_start_month_name.lower(), cal_start_month_name.lower()).lower()
            # Convert month name to month number using datetime module
            cal_start_month_number = datetime.datetime.strptime(cal_start_month_name, "%B").month
            year = int(start_date_text.split()[-1])

            prev_button_month_xpath = f"//button[contains(@class, 'de576f5064 b46cd7aad7 e26a59bb37 c295306d66 dda427e6b5 daf5d4cb1c dd4cd5bde4 ccc6dd0abc')]"
            next_button_month_xpath = f"//button[contains(@class, 'de576f5064 b46cd7aad7 e26a59bb37 c295306d66 dda427e6b5 daf5d4cb1c dd4cd5bde4 fe489d9513')]"

            day_button_id = 'f6ec917956'

            # iterate to the correct month
            while not (start_year == year and start_date.month == cal_start_month_number):
                prev_button_month = None
                next_button_month = None
                try:
                    prev_button_month = self.driver.find_element(By.XPATH, prev_button_month_xpath)
                except:
                    print(f'Element not found or webpage not loaded in time: {prev_button_month_xpath}')

                try:
                    next_button_month = self.driver.find_element(By.XPATH, next_button_month_xpath)
                except:
                    print(f'Element not found or webpage not loaded in time: {next_button_month_xpath}')

                # iterate to the next month or previous month
                if start_year < year and start_date.month < cal_start_month_number:
                    if prev_button_month:
                        prev_button_month.click()
                elif start_year > year or start_date.month > cal_start_month_number:
                    if next_button_month:
                        next_button_month.click()

                self.random_wait()

                month_left = self.driver.find_elements(By.XPATH, calendar_container_path)[0]
                month_right = self.driver.find_elements(By.XPATH, calendar_container_path)[1]

                try:
                    month_left_label = month_left.find_element(By.XPATH, month_label_path)
                except:
                    print(f'Element not found or webpage not loaded in time: {month_label_path}')
                    self.save_screenshot()
                    raise Exception(f'Element not found or webpage not loaded in time: {month_label_path}')

                start_date_text = month_left_label.text

                cal_start_month_name = start_date_text.split()[0]
                cal_start_month_name = spanish_to_english.get(cal_start_month_name.lower(),
                                                              cal_start_month_name.lower()).lower()
                cal_start_month_number = datetime.datetime.strptime(cal_start_month_name, "%B").month
                year = int(start_date_text.split()[-1])

            # setting start date
            if start_date.month == cal_start_month_number and start_year == year:
                # select the start day
                # month_left.find_element(By.XPATH, f"//*[text()='{start_day}']").click()

                day_button = month_left.find_element(By.XPATH,
                                                     f".//*[contains(@class, '{day_button_id}') ]"
                                                     f"//span[@data-date='{start_date.year}-{start_date.month:02}-{start_date.day:02}' or text()='{start_day}']")

                # day_button.location_once_scrolled_into_view
                day_button.click()
                self.random_wait()

            # setting end date

            month_left = self.driver.find_elements(By.XPATH, calendar_container_path)[0]
            month_right = self.driver.find_elements(By.XPATH, calendar_container_path)[1]
            self.save_element_screenshot(month_left, 'month_left')
            self.save_element_screenshot(month_right, 'month_right')

            # if the end date is in the left month of the calendar
            if end_month.lower() in cal_start_month_name.lower() and end_year == year:
                # select the end day
                try:
                    day_button = month_left.find_element(By.XPATH,
                                                         f".//*[contains(@class, '{day_button_id}')]"
                                                         f"//span[@data-date='{end_date.year}-{end_date.month:02}-{end_date.day:02}' or text()='{end_day}']")

                    day_button.click()
                    self.random_wait()
                except:
                    print(f'Element not found or webpage not loaded in time: {end_day}')
                    # if this gives error is because the date is already selected.

            else:
                end_day_xpath = f".//*[contains(@class, '{day_button_id}')]//span//span[text()='{end_day}']"
                try:

                    # we look in the right calendar month
                    day_button = month_right.find_elements(By.XPATH, end_day_xpath)

                    if day_button.__len__() > 1:
                        self.save_element_screenshot(day_button[1], f"end_day_button_{end_day}")
                        self.driver.execute_script("arguments[0].click();", day_button[1])
                        # day_button[1].click()
                    else:
                        self.save_element_screenshot(day_button[0], f"end_day_button_{end_day}")
                        self.driver.execute_script("arguments[0].click();", day_button[0])
                        # day_button[0].click()
                    self.random_wait()
                except Exception as e:
                    print(e)
                    print(f'Element not found or webpage not loaded in time: {end_day_xpath}')
                    # if this gives error is because the date is already selected.

            # calendar_done_button_xpath = f"//*[contains(@class, 'calendar-footer')]//button"
            # try:
            #     calendar_done_button = self.driver.find_element(By.XPATH, calendar_done_button_xpath)
            # except:
            #     print(f'Element not found or webpage not loaded in time: calendar_done_button')
            # calendar_done_button.click()
            # self.random_wait()

            # self.save_screenshot("date_part")

        date_part()

        # *** Entering GUESTS ***
        def rooms_part():
            room_picker_data_xpath = f"//*[contains(@class, 'a83ed08757 ebbedaf8ac ada2387af8') or @data-testid='occupancy-config']"
            try:
                button_room_picker = self.wait.until(EC.presence_of_element_located((By.XPATH, room_picker_data_xpath)))
            except:
                print(f'Element not found or webpage not loaded in time: {room_picker_data_xpath}')
                self.save_screenshot()
                raise Exception(f'Element not found or webpage not loaded in time: {room_picker_data_xpath}')

            button_room_picker.click()

            self.random_wait()

            room_controls_xpath = (f"//div[contains(@class, 'f766b6b016 aad29c76fe') or @data-testid='occupancy-popup']"
                                   f"//*[@class='a9669463b9']")
            room_controls = self.driver.find_elements(By.XPATH, room_controls_xpath)

            # room_controls_footer_xpath = f"//div[contains(@class, 'distribution__container')]//*[contains(@class,'stepper__room__footer')]"
            # room_controls_footer = self.driver.find_element(By.XPATH, room_controls_footer_xpath)
            # logger.info(f"room_controls: {room_controls.__len__()}")

            # remove_adults_xpath = f".//descendant::button[1]"
            adults_input_xpath = f".//*[contains(@class, 'e484bb5b7a')]//span[contains(@class, 'e32aa465fd')]"
            # adults_input = self.wait.until(EC.presence_of_element_located((By.XPATH, adults_input_xpath)))
            adult_control = room_controls[0]
            adults_input = adult_control.find_element(By.XPATH, adults_input_xpath)

            # increase_adults_xpath = f".//descendant::button[2]"
            remove_adults_xpath = f".//button[contains(@class,'de576f5064 b46cd7aad7 e26a59bb37 c295306d66 c7a901b0e7 aaf9b6e287 c857f39cb2')]"
            increase_adults_xpath = f".//button[contains(@class,'de576f5064 b46cd7aad7 e26a59bb37 c295306d66 c7a901b0e7 aaf9b6e287 dc8366caa6')]"
            if adults and adults >= 1:
                current_adults = int(adults_input.text)
                while current_adults != adults:
                    remove_adult_button = adult_control.find_element(By.XPATH, remove_adults_xpath)
                    add_adult_button = adult_control.find_element(By.XPATH, increase_adults_xpath)

                    if current_adults < adults:
                        add_adult_button.click()
                    else:
                        remove_adult_button.click()

                    self.random_wait()

                    adults_input = self.wait.until(EC.presence_of_element_located((By.XPATH, adults_input_xpath)))
                    current_adults = int(adults_input.text)

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

                increase_children_xpath = f".//button[contains(@class,'de576f5064 b46cd7aad7 e26a59bb37 c295306d66 c7a901b0e7 aaf9b6e287 dc8366caa6')]"
                # # add adult
                # add_adult_button = self.driver.find_element(By.XPATH, f"//*[@aria-describedby='adultCountLabel']")
                # add_adult_button.click()

                for i in range(children):
                    add_children_button = room_controls[1].find_element(By.XPATH, increase_children_xpath)
                    if add_children_button.is_enabled():
                        print(f"add children {i}")
                        add_children_button.click()
                        self.random_wait()

                try:
                    while True:
                        children_ages = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, f".//*[@data-testid='kids-ages' or contains(@class, 'b057a7359f')]"
                                                                            f"//div[@data-testid='kids-ages-select' or contains(@class,'e2585683de be323bc46b c9abb9ab2f')]"
                                                                            f"//select[@name='age' or contains(@class,'ef7e348457')]")))
                        Select(children_ages[0]).select_by_value("10")
                except:
                    print("No children ages found")


            guest_done_button_xpath = f"//button[contains(@class, 'de576f5064 b46cd7aad7 e26a59bb37 c295306d66 c7a901b0e7 aaf9b6e287 dc8366caa6') or contains(text(), 'Done') or contains(text(), 'OK')]"
            try:
                done_button = self.driver.find_element(By.XPATH, guest_done_button_xpath)
                done_button.click()
            except:
                print(f'Element not found or webpage not loaded in time: {guest_done_button_xpath}')

            self.random_wait()

            # self.save_screenshot("rooms_part")

        rooms_part()

        search_button_xpath = (f"//div[@data-testid='searchbox-layout-wide']//span[contains(text(), 'Search') or contains(text(), 'Buscar') or contains(@class, 'e4adce92df')]")

        try:
            search_button = self.wait.until(EC.presence_of_element_located((By.XPATH, search_button_xpath)))
        except:
            print(f'Element not found or webpage not loaded in time: {search_button_xpath}')
            self.save_screenshot()
            raise Exception(f'Element not found or webpage not loaded in time: {search_button_xpath}')

        search_button.click()

        self.random_wait()

        # self.save_screenshot("search_button")

        # map_full_overlay_xpath = f"//*[contains(@class, 'map_full_overlay__close') and contains(@role, 'button')]"
        # self.click_element(map_full_overlay_xpath, raise_exception=False)

        modal_xpath = f"//*[contains(@aria-label, '')]"
        self.wait_and_click_element(modal_xpath, raise_exception=False)

        map_modal_close_xpath = f"//*[@id='b2searchresultsPage']//button[contains(@class, 'map-modal')]"
        self.wait_and_click_element(map_modal_close_xpath, raise_exception=False)

        self.wait_and_click_element(map_modal_close_xpath, raise_exception=False)
        self.close_sign_up()

        # get the first hotel in the listing result
        property_listing_result_xpath = f"//*[@data-testid='property-card']"
        try:
            # Wait up to 10 seconds before throwing a TimeoutException unless it finds the element to return within 10 seconds
            results_property = self.wait.until(
                EC.presence_of_all_elements_located((By.XPATH, property_listing_result_xpath))
            )
        except:
            logger.debug(f'Element not found or webpage not loaded in time: {property_listing_result_xpath}')
            self.save_screenshot()
            raise Exception(f'Element not found or webpage not loaded in time: {property_listing_result_xpath}')

        self.random_wait()

        # property_class = 'uitk-spacing uitk-spacing-margin-blockstart-three'
        # results_property = self.driver.find_element(By.XPATH,
        #                                             f"//*[@data-stid='{property_listing_result_stid}']") \
        #                               .find_elements(By.XPATH,
        #                                              f".//div[@class='{property_class}']")

        # data-test-id="price-summary" # we can look for this.

        negative_theme_xpath = f".//*[contains(@class, 'e2585683de ca4ca01afd')]"  # sin disponibilidad / we are sold out

        logger.info(f"Current URL: {self.driver.current_url}")

        found = False
        for i in range(results_property.__len__()):
            result_element = results_property[i]

            # print(f"title_element_text: {title_element.text}")
            found_elements = location.lower() in result_element.text.lower()

            if found_elements:
                logger.debug(f"found location: {location} in {result_element.text}")

                try:
                    sold_out = result_element.find_element(By.XPATH, negative_theme_xpath)

                    if sold_out:
                        logger.debug(f"Sold out")
                        continue
                        # yield item

                except NoSuchElementException:
                    logger.debug("Not sold out.")

                if result_element.is_enabled():
                    logger.debug(f"click room {i}")

                    # Now, you can clear the request history
                    del self.driver.requests

                    result_element.location_once_scrolled_into_view
                    self.save_screenshot()
                    title_element = result_element.find_element(By.XPATH, ".//*[@data-testid='title']")
                    title_element.click()
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

                    logger.debug(f"switch_to.window")

                    found = True
                    break

        if not found:
            print(f"not found {location}")
            self.save_screenshot()
            raise Exception(f"not found {location}")

        section_room_xpath = f"//table[contains(@id, 'hprt-table') or contains(@class, 'hprt-table')]"
        rooms_table = self.wait_for_element(section_room_xpath)
        # Find all rows in the table
        rows = rooms_table.find_elements(By.XPATH, ".//tbody/tr//*[contains(@class,'-first')]/parent::*")

        self.driver.implicitly_wait(10)

        self.close_sign_up()

        response = {
            "success": True,
            "search_criteria": params,
            "hotel": location,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
        }

        rooms = []

        # we do this to trigger the query of fragments requests
        # Scroll to each row, waiting 1 second between each
        for row in rows:
            # self.driver.execute_script("arguments[0].scrollIntoView();", row)
            row.location_once_scrolled_into_view
            self.random_wait()
            room_name_element = row.find_element(By.XPATH, ".//*[contains(@class, 'hprt-roomtype-icon-link')]")
            room_price = row.find_element(By.XPATH, ".//*[contains(@class, 'prco-valign-middle-helper')]")
            pr = room_price.text
            price = int(''.join(filter(str.isdigit, pr)))
            room = {
                'name': room_name_element.text,
                'price': price # .get_attribute("data-hotel-rounded-price"),
            }

            # beds_type = row.find_elements(By.XPATH, ".//*[contains(@class, 'rt-bed-types')]")
            beds_elements = row.find_elements(By.XPATH, ".//*[contains(@class, 'hprt-roomtype-bed')]//ul[contains(@class, 'rt-bed-types')]/li[contains(@class, 'rt-bed-type')]/span")
            if not beds_elements:
                beds_elements = row.find_elements(By.XPATH, ".//*[contains(@class, 'hprt-roomtype-bed')]//ul[contains(@class, 'room-config')]/li[contains(@class, 'bedroom_bed_type')]/span")

            beds = []
            for bed_element in beds_elements:
                beds.append(bed_element.text)

            room['beds'] = beds
            rooms.append(room)

        response['rooms_found'] = rooms.__len__()
        response['currency_prices'] = 'USD'
        response['rooms'] = rooms

        # response = self.process_requests()

        self.exit_driver()

        return response

    def process_requests(self):
        response = {}

        filtered_requests = []
        for request in self.driver.requests:
            # if ('/fragment.json' in request.path or '/fragment.es-mx.json' in request.path) \
            #         or '/hotel/mx/' in request.path:
            #     filtered_requests.append(request)
            '''
                https://www.booking.com/hotel/pr/ac-hotel-marriott-san-juan.es-mx.html?aid=304142&label=gen173nr-1FCAEoggI46AdIM1gEaKABiAEBmAFSuAEZyAEM2AEB6AEB-AEDiAIBqAIDuALxoeO7BsACAdICJDMwYjhjZmRjLTNkOGUtNDM0Zi1hMzdjLTI5YjUyMDRhNGIyMNgCBeACAQ&sid=9c31748321271e3308a4bc1b7c7d032d&all_sr_blocks=49422307_98299434_2_2_0&checkin=2025-02-06&checkout=2025-02-12&dest_id=494223&dest_type=hotel&dist=0&group_adults=2&group_children=0&hapos=1&highlighted_blocks=49422307_98299434_2_2_0&hpos=1&matching_block_id=49422307_98299434_2_2_0&no_rooms=1&req_adults=2&req_children=0&sb_price_type=total&sr_order=popularity&sr_pri_blocks=49422307_98299434_2_2_0__204600&srepoch=1735971084&srpvid=ce392b84fa0406ad&type=total&ucfs=1&

                https://www.booking.com/dml/graphql?aid=304142
                &label=gen173nr-1FCAEoggI46AdIM1gEaKABiAEBmAExuAEZyAEM2AEB6AEB-AEDiAIBqAIDuAL708q7BsACAdICJGZmYmZjN2U1LTQwNzktNDM5Ni1hM2RhLTkzODU2NDQ5YjFkNdgCBeACAQ&sid=495938963776f8044cc62a3210c6ac89&all_sr_blocks=49422307_98299434_2_2_0
                &checkin=2025-02-06&checkout=2025-02-12
                &dest_id=494223
                &dest_type=hotel&dist=0
                &group_adults=2&group_children=0
                &hapos=1&highlighted_blocks=49422307_98299434_2_2_0&hpos=1&matching_block_id=49422307_98299434_2_2_0&no_rooms=1&req_adults=2&req_children=0&room1=A%2CA&sb_price_type=total&sr_order=popularity&sr_pri_blocks=49422307_98299434_2_2_0__200600&srepoch=1735567993&srpvid=db6063e28be408ef&type=total&ucfs=1&lang=en-us
            '''
            if ('/dml/graphql?' in request.path
                    and all(item in request.path for item in ['dest_type=hotel', f'checkin=', f'checkout='])
                and "roomDetail" in self.decode_body(request.body)
                    and "" in self.decode_body(request.body)
            ):
                filtered_requests.append(request)

        logger.debug(f"requests found: {filtered_requests.__len__()} out of {self.driver.requests.__len__()}")

        result_body = []
        # data_found = False
        # if filtered_requests.__len__() == 1:
        #     request = filtered_requests[0]
        #
        #     response_body = self.decode_body(request.response)
        #
        #     # Parse the request body as JSON
        #     body = json.loads(response_body)
        #
        #     # if body is a list get the first element
        #     if isinstance(body, list):
        #         body = body[0]
        #
        #     response = self.standardize_data(body)
        #
        #     data_found = True
        #     print(
        #         'Request URL:', request.url,
        #         '\nResponse status:', request.response.status_code,
        #         # '\nResponse body:', request.response.body
        #     )

        data_found = False
        body_html = None
        for request in filtered_requests:

            response_body = decode(request.response.body,
                                   request.response.headers.get('Content-Encoding', 'application/json; charset=utf-8'))

            if '/hotel/mx/' in request.path:
                if request.response.status_code == 200:
                    body_html = response_body
                continue

            # Parse the request body as JSON
            body = json.loads(response_body)

            # if body is a list get the first element
            if isinstance(body, list):
                body = body[0]

            if 'status' not in body or body['status'] != 200 or not body['data']:
                # print(f'No data found')
                continue

            result_body.append(body)
            # response = body

            data_found = True
            logger.debug(f"Request URL: {request.url} \nResponse status:{request.response.status_code}")

            # break

        booking_js = self.driver.execute_script("return JSON.stringify(window.booking.env);")
        booking_metadata = json.loads(booking_js)

        if result_body.__len__() > 0:
            # response = {'data': result_body}
            response = self.standardize_data(result_body, booking_metadata)

        # if body_html:
        #     response['html_data'] = body_html.decode('utf-8')

        if not data_found:
            self.save_screenshot()
            raise Exception(f"Data not found")

        return response

    def standardize_data(self, data, metadata=None):
        return get_standard_data_booking(data, self.params, metadata=metadata)

    def close_sign_up(self):
        close_modal_sign_up_xpath = f"//*[contains(@class, 'a83ed08757 c21c56c305 f38b6daa18 d691166b09 ab98298258 f4552b6561') and contains(@aria-label, 'Dismiss sign-in info')]"
        close_modal_sign_up = None
        try:
            logger.debug(f'waiting for: {close_modal_sign_up_xpath}')
            # Wait for actions to complete
            close_modal_sign_up = self.wait.until(EC.presence_of_element_located((By.XPATH, close_modal_sign_up_xpath)))
        except:
            logger.debug(f'Element not found or webpage not loaded in time: {close_modal_sign_up_xpath}')
            # self.save_screenshot()
            # raise Exception(f'Element not found or webpage not loaded in time: {close_modal_sign_up_xpath}')
        if close_modal_sign_up:
            close_modal_sign_up.click()
