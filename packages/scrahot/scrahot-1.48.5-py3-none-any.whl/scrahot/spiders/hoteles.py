import calendar
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
from scrahot.standard_json import get_standard_data
from scrahot.utils import XHRListener
import seleniumbase

class HotelesSeleniumBase(BaseSelenium):
    def __init__(self):
        super().__init__('sb')

        self.name = 'hoteles'

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
                              maximize=True, timeout_multiplier=3, save_screenshot=True) as sb):
            try:
                url = 'https://hoteles.com'
                sb.activate_cdp_mode(url)
                sb.sleep(2.5)

                # Select currency
                self.select_currency_process(sb)

                def location_part():
                    # Enter Location
                    # location_btn
                    sb.cdp.click(
                        # '//*[@data-stid="destination_form_field-menu-trigger" or @data-stid="location-field-destination-menu-trigger" or @data-stid="destination_form_field-dialog-trigger
                        '#lodging_search_form > div > div > div:nth-child(1) > div > div > div > div.uitk-field.has-floatedLabel-label.has-icon > button'
                    )
                    sb.sleep(1)

                    sb.cdp.type('#destination_form_field', location)
                    # dest_field = sb.cdp.find_element(
                    #     '#destination_form_field'
                    # )
                    # dest_field.send_keys(location)
                    sb.sleep(3)

                    suggestion = sb.cdp.find_element(
                        # '#lodging_search_form > div > div > div:nth-child(1) > div > div > div > section > div > div.uitk-scrollable.uitk-scrollable-vertical > div > div > ul > div:nth-child(1) > li > div > div > button'
                        'div[data-stid="search-location"] button[data-stid="destination_form_field-result-item-button"]',
                        timeout=30
                    )
                    suggestion.click()
                    sb.sleep(1)

                location_part()

                def calendar_part():
                    # Enter Dates
                    # date_field
                    sb.cdp.click(
                        'button[data-stid="uitk-date-selector-input1-default"]'
                    )
                    sb.sleep(1)

                    prev_btn = sb.cdp.find_element(
                        'button[data-stid="uitk-calendar-navigation-controls-previous-button"]')
                    next_btn = sb.cdp.find_element('button[data-stid="uitk-calendar-navigation-controls-next-button"]')

                    month_left_xpath = f"[@class='uitk-month uitk-month-double uitk-month-double-left']"
                    month_right_xpath = f"[@class='uitk-month uitk-month-double uitk-month-double-right']"
                    month_left, month_right = self.get_months_container(sb)

                    month_label_selector = f"[class='uitk-align-center uitk-month-label']"
                    month_label = month_left.query_selector(month_label_selector)
                    spanish_to_english = {
                        'enero': 'January', 'febrero': 'February', 'marzo': 'March',
                        'abril': 'April', 'mayo': 'May', 'junio': 'June',
                        'julio': 'July', 'agosto': 'August', 'septiembre': 'September',
                        'octubre': 'October', 'noviembre': 'November', 'diciembre': 'December'
                    }

                    current_month = spanish_to_english.get(month_label.text.split()[0].lower(),
                                                           month_label.text.split()[0].lower())
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
                        month_label = month_left.query_selector(
                            month_label_selector)
                        current_month = spanish_to_english.get(month_label.text.split()[0].lower(),
                                                               month_label.text.split()[0].lower())
                        current_year = int(month_label.text.split()[-1])

                    # Select dates
                    day_filter = ('(contains(@class, "uitk-date-number") '
                                  'or contains(@class, "uitk-date-picker-day-number") '
                                  'or contains(@class, "uitk-date-picker-day") '
                                  'or contains(@class, "uitk-day"))')
                    # day_filter = '[class*="uitk-date-number"], [class*="uitk-date-picker-day-number"], [class*="uitk-date-picker-day"], [class*="uitk-day"]'
                    month_left, month_right = self.get_months_container(sb)
                    start_day_btn = sb.cdp.find_element(
                        # f'//*[(text()="{start_day}" or @data-day="{start_day}")]'
                        f'//*{month_left_xpath}//*[(text()="{start_day}" or @data-day="{start_day}")]'
                    )

                    start_day_btn.click()
                    sb.sleep(1)
                    month_left, month_right = self.get_months_container(sb)
                    if end_date.month == start_date.month and end_date.year == start_year:
                        end_day_btn = sb.cdp.find_element(
                            # f'//*[{day_filter} and (text()="{end_day}" or @data-day="{end_day}")]'
                            f'//*{month_left_xpath}//*[{day_filter} and (text()="{end_day}" or @data-day="{end_day}")]'
                        )
                    else:
                        end_day_btn = sb.cdp.find_element(
                            # f'//*[{day_filter} and (text()="{end_day}" or @data-day="{end_day}")]')
                            f'//*{month_right_xpath}//*[{day_filter} and (text()="{end_day}" or @data-day="{end_day}")]')
                    end_day_btn.click()
                    sb.sleep(1)

                    # dont_btn
                    # done_btn
                    # sb.cdp.scroll_into_view('[data-stid="apply-date-selector"]')
                    try:
                        sb.cdp.click("[class*='onetrust-close-btn-handler onetrust-close-btn-ui banner-close-button ot-close-icon']")
                    except Exception as e:
                        logger.debug(f"not banner to close")

                    try:
                        sb.cdp.click('[data-stid="apply-date-selector"]')
                        sb.sleep(1)
                    except Exception as e:
                        logger.info(f"apply date not clicked")

                calendar_part()

                def rooms_part():
                    # Enter Guests
                    # guest_field
                    guest_field = sb.cdp.click(
                        # '//*[contains(@data-stid, "open-room-picker") or contains(@data-testid, "travelers-field")]'
                        '#lodging_search_form > div > div > div:nth-child(3) > div > div.uitk-field.has-floatedLabel-label.has-icon.has-placeholder > button'
                    )
                    sb.sleep(1)

                    room_controls_selector = '#lodging_search_form > div > div > div:nth-child(3) > div > div.uitk-menu-container.uitk-menu-open.uitk-menu-pos-right.uitk-menu-container-autoposition.uitk-menu-container-has-intersection-root-el > div > div > section > div.uitk-spacing.uitk-spacing-padding-blockstart-unset > div:nth-child(2) > div > div'
                    room_controls = sb.cdp.select_all(
                        # '//*[contains(@class,"uitk-layout-flex uitk-layout-flex-item uitk-step-input-controls")]'
                        room_controls_selector
                    )
                    adults_input = room_controls[0].query_selector(
                        # './/input[contains(@id, "adult-input-0") or contains(@id, "traveler_selector_adult_step_input-0")]'
                        f'input[id*="adult-input-0"], input[id*="traveler_selector_adult_step_input-0"]'
                    )
                    current_adults = int(adults_input.get_attribute("value"))

                    # remove_btn = room_controls[0].query_selector('.//button[contains(@class,"uitk-step-input-touch-target")][1]')
                    # add_btn = room_controls[0].query_selector('.//button[contains(@class,"uitk-step-input-touch-target")][2]')
                    remove_btn = room_controls[0].query_selector('button.uitk-step-input-touch-target:nth-of-type(1)')
                    add_btn = room_controls[0].query_selector('button.uitk-step-input-touch-target:nth-of-type(2)')

                    while current_adults != adults:
                        if current_adults < adults:
                            add_btn.click()
                        else:
                            remove_btn.click()
                        sb.sleep(1)
                        # adults_input = room_controls[0].query_selector(
                        #     './/input[contains(@id, "adult-input-0") or contains(@id, "traveler_selector_adult_step_input-0")]')
                        adults_input = room_controls[0].query_selector(
                         'input[id*="adult-input-0"], input[id*="traveler_selector_adult_step_input-0"]')
                        current_adults = int(adults_input.get_attribute("value"))

                    if children > 0:
                        # add_child_btn = room_controls[1].query_selector(
                        #     './/button[contains(@class,"uitk-step-input-touch-target")][2]')
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

                rooms_part()

                # Search
                # search_btn
                # sb.cdp.click('//*[contains(@id,"search_button") or contains(@data-testid, "submit-button")]')
                sb.cdp.click('#search_button, [data-testid="submit-button"]')
                sb.sleep(3)

                for i in range(10):
                    sb.cdp.scroll_down(8)

                try:
                    sb.cdp.click('#close-fee-inclusive-pricing-sheet', timeout=30)
                    sb.sleep(1)
                except Exception as e:
                    logger.info(f"Error closing fee-inclusive pricing sheet: {e}")

                # Find hotel
                hotel_cards = sb.cdp.select_all(
                    # '//div[@data-stid="section-results"]//div[@data-stid="property-listing-results"]//div[@class="uitk-spacing uitk-spacing-margin-blockstart-three"]'
                    'div[data-stid="section-results"] div[data-stid="property-listing-results"] div.uitk-spacing.uitk-spacing-margin-blockstart-three'
                )
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
                all_rooms = sb.cdp.select_all('[data-stid="section-room-list"] > div > div', timeout=30)
                for room in all_rooms:
                    try:
                        # room = all_rooms.query_selector(f'{room_child.attrs.class_.replace(" ", ".")}')
                        room.scroll_into_view()

                        sb.sleep(0.5)

                        # description = ''
                        # buttons = room.query_selector_all('div.room-card__title__button > button')
                        # button_info = buttons[1] if len(buttons) > 1 else None
                        # if button_info:
                        #     button_info.mouse_click()
                        #
                        #     description = sb.cdp.find_element('div.MuiDialogContent-root > div:nth-child(2) span').text
                        #     sb.cdp.click('[data-testid="close-room-detail"]')

                        # price_element = room.query_selector('[data-test-id="price-summary-message-line"] > div:nth-child(1) span') # per night
                        price_element = room.query_selector('[data-test-id="price-summary-message-line"]:nth-of-type(2) .uitk-text') # total nights
                        if not price_element:
                            logger.debug(f"No price found for room {room}")
                            continue
                        price = re.sub(r'[^\d.,]', '', price_element.text).replace('.', '').replace(',', '.')

                        more_details = room.query_selector('button[class="uitk-link uitk-link-align-left uitk-link-layout-default uitk-link-medium"]')
                        more_details.click()
                        sb.sleep(0.5)

                        name = sb.cdp.find_element('div[data-stid="property-offers-details-dialog-header"] > h3').text.strip()
                        description = sb.cdp.select_all(
                            # '[class="uitk-spacing uitk-spacing-padding-inline-three"] [class="uitk-typelist-item uitk-typelist-item-bullet-icon-alternate uitk-typelist-item-bullet-icon uitk-typelist-item-orientation-stacked uitk-typelist-item-size-2 uitk-typelist-item-bullet-icon-default-theme uitk-typelist-item-indent"]:nth-child(4)'
                            '[class="uitk-spacing uitk-spacing-padding-inline-three"] [class="uitk-typelist-item uitk-typelist-item-bullet-icon-alternate uitk-typelist-item-bullet-icon uitk-typelist-item-orientation-stacked uitk-typelist-item-size-2 uitk-typelist-item-bullet-icon-default-theme uitk-typelist-item-indent"]'
                            )

                        close_button = sb.cdp.find_element('button[class="uitk-toolbar-button uitk-toolbar-button-icon-only"]')
                        close_button.click()
                        sb.sleep(0.5)

                        room = {
                            "name": name,
                            "beds": [x.text for x in description if 'bed' in x.text.lower() or 'cama' in x.text.lower()],
                            "price": price,
                        }
                        rooms.append(room)
                    except Exception as e:
                        logger.warning(f"Skipping room due to error: {e}")
                        continue

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

    def select_currency_process(self, sb):
        # currency_btn
        sb.cdp.click('//button[@data-stid="button-type-picker-trigger"]')
        sb.sleep(1)

        # currency_select
        # sb.cdp.select_option_by_text('#site-selector', "United States · USD $")
        sb.select_option_by_value('#site-selector', "300000001")
        sb.sleep(2)

        # save_btn
        sb.cdp.mouse_click('(//section[@role="dialog"]//button)[last()]')
        sb.sleep(2)

    def get_months_container(self, sb):
        month_left_xpath = f"[class='uitk-month uitk-month-double uitk-month-double-left']"
        month_right_xpath = f"[class='uitk-month uitk-month-double uitk-month-double-right']"

        month_left = sb.cdp.find_element(month_left_xpath)
        month_right = sb.cdp.find_element(month_right_xpath)

        return month_left, month_right

    def standardize_data(self, data):
        return get_standard_data(data, self.params)

#
# class HotelesSelenium(BaseSelenium):
#
#     def __init__(self):
#         super().__init__()
#
#         self.name = 'hoteles'
#
#         # Only request URLs containing "hoteles" or "whatever" will now be captured
#         self.driver.scopes = [
#             '.*hoteles\.*',
#             '.*hotels\.*',
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
#         url = 'https://hoteles.com'
#         self.driver.get(url)
#
#         logger.debug(f'url: {url}')
#
#         # self.save_screenshot()
#
#         self.select_currency_process()
#
#         # Entering LOCATION
#         location_button_data_stid = 'destination_form_field-menu-trigger'
#         try:
#             # Wait up to 10 seconds before throwing a TimeoutException unless it finds the element to return within 10 seconds
#             button = self.wait.until(
#                 EC.presence_of_element_located((By.XPATH, f"//*[@data-stid='{location_button_data_stid}']"))
#             )
#         except:
#             print(f'Element not found or webpage not loaded in time: {location_button_data_stid}')
#
#             location_button_data_stid = 'destination_form_field-dialog-trigger'
#             try:
#                 # Wait up to 10 seconds before throwing a TimeoutException unless it finds the element to return within 10 seconds
#                 button = self.wait.until(
#                     EC.presence_of_element_located((By.XPATH, f"//*[@data-stid='{location_button_data_stid}']"))
#                 )
#             except:
#                 print(f'Element not found or webpage not loaded in time: {location_button_data_stid}')
#                 self.save_screenshot()
#                 raise Exception(f'Element not found or webpage not loaded in time: {location_button_data_stid}')
#
#         button.click()
#
#         self.random_wait()
#
#         destination_form_field_id = 'destination_form_field'
#         # Wait for actions to complete
#         input_element = self.wait.until(
#             EC.presence_of_element_located((By.ID, destination_form_field_id))
#         )
#
#         # Input text into another element
#         input_element.send_keys(location)
#
#         self.random_wait()
#
#         input_element_selection_xpath = f"//button[contains(@data-stid, 'destination_form_field-result-item-button') or contains(@data-stid, 'location-field-destination-result-item-button')]"
#         try:
#             input_element_selection = self.wait.until(
#                 EC.presence_of_all_elements_located((By.XPATH, input_element_selection_xpath)))
#         except:
#             print(f'Element not found or webpage not loaded in time: {input_element_selection_xpath}')
#             self.save_screenshot()
#             raise Exception(f'Element not found or webpage not loaded in time: {input_element_selection_xpath}')
#         input_element_selection[0].click()
#
#         self.random_wait()
#
#         # # Simulate hitting the Enter key
#         # input_element.send_keys(Keys.ENTER)
#
#         # *** Entering DATE ***
#
#         date_button_data_xpath = f"//*[contains(@data-stid,'uitk-date-selector-input1-default') or contains(@data-stid,'open-date-picker')]"
#
#         # Find the button using its data-stid attribute and click it
#         try:
#             date_button = self.wait.until(EC.presence_of_element_located((By.XPATH, date_button_data_xpath)))
#         except:
#             print(f'Element not found or webpage not loaded in time: {date_button_data_xpath}')
#             self.save_screenshot()
#             raise Exception(f'Element not found or webpage not loaded in time: {date_button_data_xpath}')
#         date_button.click()
#
#         self.random_wait()
#
#         prev_month_button_xpath = f"//*[contains(@data-stid, 'uitk-calendar-navigation-controls-previous-button')]"
#         next_month_button_xpath = f"//*[contains(@data-stid, 'uitk-calendar-navigation-controls-next-button')]"
#
#         try:
#             # prev_button_month = self.wait.until(EC.presence_of_element_located((By.XPATH, prev_month_button_xpath)))
#             # next_button_month = self.wait.until(EC.presence_of_element_located((By.XPATH, next_month_button_xpath)))
#             prev_button_month = self.driver.find_element(By.XPATH, prev_month_button_xpath)
#             next_button_month = self.driver.find_element(By.XPATH, next_month_button_xpath)
#         except:
#             print(f'Element not found or webpage not loaded in time: {prev_month_button_xpath} or {next_month_button_xpath}')
#
#             prev_month_button_xpath = f"//*[contains(@data-stid, 'date-picker-paging')]"
#             next_month_button_xpath = f"//*[contains(@data-stid, 'date-picker-paging')]"
#             try:
#                 # prev_button_month = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, prev_month_button_xpath)))[0]
#                 # next_button_month = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, next_month_button_xpath)))[1]
#                 prev_button_month = self.driver.find_elements(By.XPATH, prev_month_button_xpath)[0]
#                 next_button_month = self.driver.find_elements(By.XPATH, next_month_button_xpath)[1]
#             except:
#                 print(f'Element not found or webpage not loaded in time: {prev_month_button_xpath} or {next_month_button_xpath}')
#                 self.save_screenshot()
#                 raise Exception('No date picker found')
#
#         month_left, month_right = self.get_months_container()
#
#         month_label_xpath = f".//*[contains(@class, 'uitk-month-label') or contains(@class, 'uitk-date-picker-month-name uitk-type-medium')]"
#         month_left_label = month_left.find_element(By.XPATH, month_label_xpath)
#         start_date_text = month_left_label.text
#         cal_start_month_name = start_date_text.split()[0]
#         spanish_to_english = {
#             'enero': 'January',
#             'febrero': 'February',
#             'marzo': 'March',
#             'abril': 'April',
#             'mayo': 'May',
#             'junio': 'June',
#             'julio': 'July',
#             'agosto': 'August',
#             'septiembre': 'September',
#             'octubre': 'October',
#             'noviembre': 'November',
#             'diciembre': 'December'
#         }
#         cal_start_month_name = spanish_to_english.get(cal_start_month_name.lower(), cal_start_month_name.lower()).lower()
#
#         # Convert month name to month number using datetime module
#         cal_start_month_number = datetime.datetime.strptime(cal_start_month_name, "%B").month
#         year = int(start_date_text.split()[-1])
#
#         # iterate to the correct month
#         while not (start_date.month == cal_start_month_number and start_year == year):
#             # iterate to the next month or previous month
#             if start_year < year and start_date.month < cal_start_month_number:
#                 prev_button_month.click()
#             elif start_year > year or start_date.month > cal_start_month_number:
#                 next_button_month.click()
#
#             self.random_wait()
#
#             month_left, month_right = self.get_months_container()
#
#             try:
#                 month_left_label = month_left.find_element(By.XPATH, month_label_xpath)
#             except:
#                 print(f'Element not found or webpage not loaded in time: {month_label_xpath}')
#                 self.save_screenshot()
#                 raise Exception(f'Element not found or webpage not loaded in time: {month_label_xpath}')
#
#             start_date_text = month_left_label.text
#
#             cal_start_month_name = start_date_text.split()[0]
#             cal_start_month_name = spanish_to_english.get(cal_start_month_name.lower(),
#                                                           cal_start_month_name.lower()).lower()
#             cal_start_month_number = datetime.datetime.strptime(cal_start_month_name, "%B").month
#             year = int(start_date_text.split()[-1])
#
#         number_filter_xpath = f"( " \
#                               f"contains(@class, 'uitk-date-number uitk-date-number-default') " \
#                               f"or contains(@class, 'uitk-date-picker-day-number') " \
#                               f"or contains(@class, 'uitk-date-picker-day') " \
#                               f"or contains(@class, 'uitk-day') " \
#                               f")"
#         # setting start date
#         if start_date.month == cal_start_month_number and start_year == year:
#             # select the start day
#             # month_left.find_element(By.XPATH, f"//*[text()='{start_day}']").click()
#             day_filter_xpath = f"(" \
#                                f"text()='{start_day}' " \
#                                f"or @data-day='{start_day}'" \
#                                f")"
#             day_button = month_left.find_element(By.XPATH, f"//*[{number_filter_xpath} and {day_filter_xpath}]")
#             day_button.click()
#             self.random_wait()
#
#         # setting end date
#
#         month_left, month_right = self.get_months_container()
#
#         # if the end date is in the left month of the calendar
#         if end_month.lower() in cal_start_month_name.lower() and end_year == year:
#             # select the end day
#             try:
#                 day_filter_xpath = f"(" \
#                                    f"text()='{end_day}' " \
#                                    f"or @data-day='{end_day}'" \
#                                    f")"
#                 day_button = month_left.find_element(By.XPATH, f"//*[{number_filter_xpath} and {day_filter_xpath}]")
#
#                 day_button.click()
#                 self.random_wait()
#             except:
#                 print(f'Element not found or webpage not loaded in time: {end_day}')
#                 # if this gives error is because the date is already selected.
#
#         else:
#             try:
#                 # we look in the right calendar month
#                 day_filter_xpath = f"(" \
#                                    f"text()='{end_day}' " \
#                                    f"or @data-day='{end_day}'" \
#                                    f")"
#                 day_button = month_right.find_elements(By.XPATH,
#                                                   f"//*[{number_filter_xpath} and {day_filter_xpath}]")
#
#                 if day_button.__len__() > 1:
#                     day_button[1].click()
#                 else:
#                     day_button[0].click()
#                 self.random_wait()
#             except:
#                 print(f'Element not found or webpage not loaded in time: {end_day}')
#                 # if this gives error is because the date is already selected.
#
#         calendar_done_button_xpath = f"//section[contains(@data-testid, 'popover-sheet')]//footer//button[contains(@class, 'uitk-button')]"
#         try:
#             # calendar_done_button = self.wait.until(EC.presence_of_element_located((By.XPATH, calendar_done_button_xpath)))
#             calendar_done_button = self.driver.find_element(By.XPATH, calendar_done_button_xpath)
#         except:
#             print(f'Element not found or webpage not loaded in time: {calendar_done_button_xpath}')
#             calendar_done_button_xpath = f"//button[contains(@data-stid, 'apply-date-picker')]"
#             try:
#                 # calendar_done_button = self.wait.until(EC.presence_of_element_located((By.XPATH, calendar_done_button_xpath)))
#                 calendar_done_button = self.driver.find_element(By.XPATH, calendar_done_button_xpath)
#             except:
#                 self.save_screenshot()
#                 raise Exception(f'Element not found or webpage not loaded in time: {calendar_done_button_xpath}')
#         calendar_done_button.click()
#         self.random_wait()
#
#         # Entering GUESTS
#         room_picker_data_stid = 'open-room-picker'
#         try:
#             button_room_picker = self.driver.find_element(By.XPATH, f"//*[@data-stid='{room_picker_data_stid}']")
#         except:
#             print(f'Element not found or webpage not loaded in time: {room_picker_data_stid}')
#             self.save_screenshot()
#             raise Exception(f'Element not found or webpage not loaded in time: {room_picker_data_stid}')
#         button_room_picker.click()
#
#         self.random_wait()
#
#         increase_adults_class = 'uitk-layout-flex uitk-layout-flex-item uitk-step-input-controls'
#
#         remove_adult_button = self.driver.find_element(By.XPATH,
#                                                        f"//*[@class='{increase_adults_class}']/descendant::button[1]")
#         for i in range(1):
#             if remove_adult_button.is_enabled():
#                 print(f"remove adult {i}")
#                 remove_adult_button.click()
#                 self.random_wait()
#
#         if adults and adults > 1:
#
#             # add adult
#             add_adult_button = self.driver.find_element(By.XPATH,
#                                                         f"//*[@class='{increase_adults_class}']/descendant::button[2]")
#
#             # for each adults
#             for i in range(adults - 1):
#                 print(f"add adult {i}")
#                 add_adult_button.click()
#                 self.random_wait()
#
#         if children and children > 0:
#             increase_children_class = 'uitk-layout-flex uitk-layout-flex-item uitk-step-input-controls'
#             # # add adult
#             # add_adult_button = self.driver.find_element(By.XPATH, f"//*[@aria-describedby='adultCountLabel']")
#             # add_adult_button.click()
#             add_children_button = self.driver.find_elements(By.XPATH,
#                                                             f"//*[@class='{increase_children_class}']/descendant::button[2]")[
#                 1]
#             for i in range(children):
#                 if add_children_button.is_enabled():
#                     print(f"remove adult {i}")
#                     add_children_button.click()
#                     self.random_wait()
#
#             children_ages_xpath = f"//select[contains(@class,'age-traveler_selector_children_age_selector') or contains(@name,'child-traveler_selector_children_age_selector')]"
#             children_ages = self.driver.find_elements(By.XPATH, children_ages_xpath)
#
#             for i in range(children_ages.__len__()):
#                 Select(children_ages[i]).select_by_value("10")
#
#         guest_done_button_id = 'traveler_selector_done_button'
#         done_button = self.driver.find_element(By.ID, guest_done_button_id)
#         done_button.click()
#
#         search_button_id = 'search_button'
#         search_button = self.driver.find_element(By.ID, search_button_id)
#         search_button.click()
#
#         # get the first hotel in the listing result
#
#         property_listing_result_xpath = f"//*[@data-stid='property-listing-results']"
#
#         try:
#             # Wait up to 10 seconds before throwing a TimeoutException unless it finds the element to return within 10 seconds
#             property_listing_result = self.wait.until(EC.presence_of_element_located((By.XPATH, property_listing_result_xpath)))
#         except:
#             print(f'Element not found or webpage not loaded in time: {property_listing_result_xpath}')
#             self.save_screenshot()
#             raise Exception(f'Element not found or webpage not loaded in time: {property_listing_result_xpath}')
#
#         property_elements_xpath = f".//div[@class='uitk-spacing uitk-spacing-margin-blockstart-three' and not(contains(@data-stid, 'banner'))]"
#         results_property = property_listing_result.find_elements(By.XPATH, property_elements_xpath)
#
#         # data-test-id="price-summary" # we can look for this.
#
#         negative_theme_xpath = f".//*[@class='uitk-text-negative-theme']"  # sin disponibilidad / we are sold out
#
#         found = False
#         for i in range(results_property.__len__()):
#             result_element = results_property[i]
#
#             found_elements = location.lower() in result_element.text.lower()
#
#             if found_elements:
#                 print(f"found location: {location} in {result_element.text}")
#
#                 try:
#                     sold_out = result_element.find_element(By.XPATH, negative_theme_xpath)
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
#                     new_window_handle = [handle for handle in self.driver.window_handles if handle != original_window_handle][0]
#                     self.driver.switch_to.window(new_window_handle)
#
#                     found = True
#                     break
#
#         self.random_wait()
#
#         if not found:
#             print(f"not found {location}")
#             self.save_screenshot()
#             raise Exception(f"not found {location}")
#
#         self.driver.implicitly_wait(10)
#
#         section_room_list = 'section-room-list'
#         try:
#             # Wait up to 10 seconds before throwing a TimeoutException unless it finds the element to return within 10 seconds
#             self.wait.until(
#                 EC.presence_of_element_located((By.XPATH, f"//*[@data-stid='{section_room_list}']"))
#             )
#         except:
#             print(f'Element not found or webpage not loaded in time: {section_room_list}')
#             self.save_screenshot()
#             raise Exception(f'Element not found or webpage not loaded in time: {section_room_list}')
#
#         # Get the json result using the proxy solution found
#
#         response = self.process_requests()
#
#         self.exit_driver()
#
#         return response
#
#     def process_requests(self):
#         response = {}
#         prefilt = [request for request in self.driver.requests if '/graphql' in request.path]
#         filtered_requests = []
#         for request in prefilt:
#             if '/graphql' in request.path:
#                 body = None
#
#                 if request.body:
#                     # Parse the request body as JSON
#                     body = json.loads(request.body)
#
#                 # if body is a list get the first element
#                 if isinstance(body, list):
#                     body = body[0]
#
#                 if body and body.get('operationName', '').lower() == 'AncillaryPropertyOffersQuery'.lower():
#                     filtered_requests.append(request)
#
#         data_found = False
#         # Now you can inspect the requests
#         for request in filtered_requests:
#             # graphql_query = '"operationName":"PropertyOffersQuery"'  # 'PropertyOffersQuery'
#             if request.response and request.body:
#                 try:
#                     response_body = decode(request.response.body,
#                                            request.response.headers.get('Content-Encoding',
#                                                                         'application/json; charset=utf-8'))
#
#                     # Parse the request body as JSON
#                     body = json.loads(response_body)
#
#                     # if body is a list get the first element
#                     if isinstance(body, list):
#                         body = [b for b in body if b.get('data', {}).get('propertyOffers', {'loading': {}}).get('loading', None) is None]
#                         body = body[0]
#
#                     # Check if the 'operationName' property exists and has the value 'PropertyOffersQuery'
#                     if "data" in body and "propertyOffers" in body['data']:
#                         data_found = True
#                         print(
#                             'Request URL:', request.url,
#                             '\nResponse status:', request.response.status_code,
#                             # '\nResponse body:', request.response.body
#                         )
#                         response = self.standardize_data(body)
#                         break
#                 except json.JSONDecodeError:
#                     # The request body could not be parsed as JSON, ignore this request
#                     pass
#
#         if not data_found:
#             self.save_screenshot()
#             raise Exception(f"Data not found")
#
#         # print(f"requests found: {filtered_requests.__len__()} out of {self.driver.requests.__len__()}")
#
#         return response
#
#     def select_currency_process(self):
#
#         select_currency_xpath = f"//button[@data-stid='button-type-picker-trigger']"
#         try:
#             self.random_wait()
#             select_currency = self.wait.until(EC.presence_of_element_located((By.XPATH, select_currency_xpath)))
#             select_currency.click()
#             self.random_wait()
#         except:
#             print(f'Element not found or webpage not loaded in time: {select_currency_xpath}')
#             self.save_screenshot()
#             raise Exception(f'Element not found or webpage not loaded in time: {select_currency_xpath}')
#
#         select_currency_xpath = f"//select[.//option[@value='300000001']]"
#         try:
#             self.random_wait()
#             select_currency = Select(self.wait.until(EC.presence_of_element_located((By.XPATH, select_currency_xpath))))
#             select_currency.select_by_value('300000001')
#             self.random_wait()
#         except:
#             print(f'Element not found or webpage not loaded in time: {select_currency_xpath}')
#             self.save_screenshot()
#             raise Exception(f'Element not found or webpage not loaded in time: {select_currency_xpath}')
#
#         select_currency_xpath = f"(//section[@role='dialog']//button)[last()]"
#         try:
#             select_currency = self.wait.until(EC.presence_of_element_located((By.XPATH, select_currency_xpath)))
#             select_currency.click()
#             self.random_wait()
#             self.random_wait()
#             self.random_wait()
#         except:
#             print(f'Element not found or webpage not loaded in time: {select_currency_xpath}')
#             self.save_screenshot()
#             raise Exception(f'Element not found or webpage not loaded in time: {select_currency_xpath}')
#
#     def get_months_container(self):
#         month_left_xpath = f"//*[@class='uitk-month uitk-month-double uitk-month-double-left']"
#         month_right_xpath = f"//*[@class='uitk-month uitk-month-double uitk-month-double-right']"
#         try:
#             # month_left = self.wait.until(EC.presence_of_element_located((By.XPATH, month_left_xpath)))
#             # month_right = self.wait.until(EC.presence_of_element_located((By.XPATH, month_right_xpath)))
#             month_left = self.driver.find_element(By.XPATH, month_left_xpath)
#             month_right = self.driver.find_element(By.XPATH, month_right_xpath)
#         except:
#             print(f'Element not found or webpage not loaded in time: {month_left_xpath} or {month_right_xpath}')
#
#             month_left_xpath = f"//*[contains(@data-stid, 'date-picker-month')]"
#             month_right_xpath = f"//*[contains(@data-stid, 'date-picker-month')]"
#             try:
#                 # month_left = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, month_left_xpath)))[0]
#                 # month_right = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, month_right_xpath)))[1]
#                 month_left = self.driver.find_elements(By.XPATH, month_left_xpath)[0]
#                 month_right = self.driver.find_elements(By.XPATH, month_right_xpath)[1]
#             except:
#                 print(f'Element not found or webpage not loaded in time: {month_left_xpath} or {month_right_xpath}')
#                 self.save_screenshot()
#                 raise Exception('No date picker found')
#         return month_left, month_right
#
#     def standardize_data(self, data):
#         return get_standard_data(data, self.params)

