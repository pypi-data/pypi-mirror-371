import datetime
import json
import re
import time

import seleniumbase
from loguru import logger
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from seleniumwire.utils import decode

from scrahot.spiders.base import BaseSelenium
from scrahot.standard_json import get_standard_data
from scrahot.utils import XHRListener


class ExpediaSeleniumBase(BaseSelenium):
    def __init__(self):
        super().__init__('sb')
        self.name = 'expedia'
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

        with (seleniumbase.SB(uc=True, test=True, locale_code="en", ad_block=True, window_size='1920,1080', maximize=True,
                              timeout_multiplier=3, save_screenshot=True) as sb):
            try:
                url = 'https://expedia.com'
                sb.activate_cdp_mode(url)
                sb.sleep(2.5)

                # Select currency
                self.select_currency_process(sb)

                # Enter Location
                # location_btn
                sb.cdp.click(
                    # '//*[@data-stid="destination_form_field-menu-trigger" or @data-stid="location-field-destination-menu-trigger" or @data-stid="destination_form_field-dialog-trigger"]'
                    '#lodging_search_form > div > div > div:nth-child(1) > div > div > div > div.uitk-field.has-floatedLabel-label.has-icon > button'
                )
                sb.sleep(1)

                dest_field = sb.cdp.find_element(
                    '#destination_form_field'
                )
                dest_field.send_keys(location)
                sb.sleep(1)

                suggestion = sb.cdp.find_element(
                    # '#lodging_search_form > div > div > div:nth-child(1) > div > div > div > section > div > div.uitk-scrollable.uitk-scrollable-vertical > div > div > ul > div:nth-child(1) > li > div > div > button'
                    'div[data-stid="search-location"] button[data-stid="destination_form_field-result-item-button"]',
                    timeout=30
                )
                suggestion.click()
                sb.sleep(1)

                # Enter Dates
                # date_field
                sb.cdp.click(
                    '[data-testid="uitk-date-selector-input1-default"]'
                )
                sb.sleep(1)

                prev_btn = sb.cdp.find_element(
                    '//*[contains(@data-stid, "uitk-calendar-navigation-controls-previous-button")]')
                next_btn = sb.cdp.find_element('//*[contains(@data-stid, "uitk-calendar-navigation-controls-next-button")]')

                # month_container = sb.cdp.find_element(
                #     '//*[@class="uitk-calendar"]/*[@class="uitk-date-picker-menu-months-container"]')
                # month_left_selector = '#lodging_search_form > div > div > div:nth-child(2) > div > section > div:nth-child(1) > div.uitk-sheet-content.uitk-date-selector-popover-content > div > div > div:nth-child(3) > div > div.uitk-month.uitk-month-double.uitk-month-double-left'
                # month_left_selector = "//*[@class='uitk-month uitk-month-double uitk-month-double-left']"
                # month_left = sb.cdp.find_element(month_left_selector)
                # month_right_selector = '#lodging_search_form > div > div > div:nth-child(2) > div > section > div:nth-child(1) > div.uitk-sheet-content.uitk-date-selector-popover-content > div > div > div:nth-child(3) > div > div.uitk-month.uitk-month-double.uitk-month-double-right'
                # month_right_selector = '#lodging_search_form > div > div > div:nth-child(2) > div > section > div:nth-child(1) > div.uitk-sheet-content.uitk-date-selector-popover-content > div > div > div:nth-child(3) > div > div.uitk-month.uitk-month-double.uitk-month-double-right'
                # month_right = sb.cdp.find_element(month_right_selector)
                month_left_xpath = f"//*[@class='uitk-month uitk-month-double uitk-month-double-left']"
                month_right_xpath = f"//*[@class='uitk-month uitk-month-double uitk-month-double-right']"
                month_left, month_right = self.get_months_container(sb)

                month_label_selector = '[class="uitk-align-center uitk-month-label"]'
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
                    month_label = month_left.query_selector(month_label_selector)
                    current_month = spanish_to_english.get(month_label.text.split()[0].lower(),
                                                           month_label.text.split()[0].lower())
                    current_year = int(month_label.text.split()[-1])

                # Select dates
                day_filter = '(contains(@class, "uitk-date-number") or contains(@class, "uitk-date-picker-day-number") or contains(@class, "uitk-date-picker-day") or contains(@class, "uitk-day"))'
                # day_filter = '[class*="uitk-date-number"], [class*="uitk-date-picker-day-number"], [class*="uitk-date-picker-day"], [class*="uitk-day"]'
                month_left, month_right = self.get_months_container(sb)
                start_day_btn = sb.cdp.find_element(
                    # f'//*[(text()="{start_day}" or @data-day="{start_day}")]'
                    f'{month_left_xpath}//*[(text()="{start_day}" or @data-day="{start_day}")]'
                )

                start_day_btn.click()
                sb.sleep(1)
                month_left, month_right = self.get_months_container(sb)
                if end_date.month == start_date.month and end_date.year == start_year:
                    end_day_btn = sb.cdp.find_element(
                        # f'//*[{day_filter} and (text()="{end_day}" or @data-day="{end_day}")]'
                        f'{month_left_xpath}//*[{day_filter} and (text()="{end_day}" or @data-day="{end_day}")]'
                    )
                else:
                    end_day_btn = sb.cdp.find_element(
                        # f'//*[{day_filter} and (text()="{end_day}" or @data-day="{end_day}")]')
                        f'{month_right_xpath}//*[{day_filter} and (text()="{end_day}" or @data-day="{end_day}")]')
                end_day_btn.click()
                sb.sleep(1)

                # dont_btn
                # done_btn
                sb.cdp.click(
                    '[data-stid="apply-date-selector"]'
                )
                sb.sleep(1)

                # Enter Guests
                # guest_field
                guest_field = sb.cdp.click(
                    # '//*[contains(@data-stid, "open-room-picker") or contains(@data-testid, "travelers-field")]'
                    '[data-stid="open-room-picker"]'
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

                # Search
                # search_btn
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
                # sb.cdp.wait_for_element_visible('[data-stid="section-room-list"] > div > div', timeout=30)
                rooms = []
                all_rooms = sb.cdp.select_all('[data-stid="section-room-list"] > div > div')
                for room in all_rooms:
                    try:
                        # room = all_rooms.query_selector(f'{room_child.attrs.class_.replace(" ", ".")}')
                        room.scroll_into_view()
                        sb.sleep(0.5)

                        negatives = room.query_selector_all(".uitk-text-negative-theme")
                        is_negative = False
                        for negative in negatives:
                            if negative and negative.text and 'We are sold out'.lower() in negative.text.lower():
                                is_negative = True
                                break

                        if is_negative:
                            logger.info(f"Skipping room because it is sold out")
                            continue

                        # description = ''
                        # buttons = room.query_selector_all('div.room-card__title__button > button')
                        # button_info = buttons[1] if len(buttons) > 1 else None
                        # if button_info:
                        #     button_info.mouse_click()
                        #
                        #     description = sb.cdp.find_element('div.MuiDialogContent-root > div:nth-child(2) span').text
                        #     sb.cdp.click('[data-testid="close-room-detail"]')

                        # price_element = room.query_selector('[data-test-id="price-summary-message-line"] > div:nth-child(1) span') # per night
                        # price_element = room.query_selector('[data-test-id="price-summary-message-line"] > div:nth-child(2) span')
                        price_element = room.query_selector_all('[data-stid="price-summary"] [class*="uitk-text uitk-type-300 uitk-text-default-theme"]')
                        if price_element and len(price_element) > 1:
                            price_element = price_element[1] # total
                        else:
                            logger.info(f"Skipping room because it is not a price element")
                            continue
                        price = re.sub(r'[^\d.,]', '', price_element.text).replace('.', '').replace(',', '.')

                        description = room.query_selector_all(
                            # 'div.uitk-layout-grid.uitk-layout-grid-has-auto-columns.uitk-layout-grid-has-columns-by-large.uitk-layout-grid-has-columns.uitk-layout-grid-has-space.uitk-layout-grid-display-grid.uitk-spacing.uitk-spacing-padding-blockstart-six ul '
                            "ul[class*='uitk-typelist uitk-typelist-orientation-stacked uitk-typelist-size-2 uitk-typelist-spacing uitk-spacing uitk-spacing-margin-blockstart-three'] li"
                        )

                        more_details = room.query_selector('button[class="uitk-link uitk-link-align-left uitk-link-layout-default uitk-link-medium"]')
                        more_details.click()
                        sb.sleep(0.5)

                        name = sb.cdp.find_element('div[data-stid="property-offers-details-dialog-header"] > h3').text.strip()


                        close_button = sb.cdp.find_element('button[class="uitk-toolbar-button uitk-toolbar-button-icon-only"]')
                        close_button.click()
                        sb.sleep(0.5)

                        room = {
                            "name": name,
                            "beds": [x.text for x in description if x and ('bed' in x.text.lower() or 'cama' in x.text.lower())],
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
                logger.error(f"Error: {type(e).__name__}: {e}", exc_info=True)


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
        sb.cdp.click('//button[@data-stid="button-type-picker-trigger"]', timeout=30)
        sb.sleep(1)

        # currency_select
        # sb.cdp.select_option_by_text('#site-selector', "United States")
        sb.select_option_by_value('#site-selector', "1", timeout=30)
        sb.sleep(1)

        # save_btn
        sb.cdp.click('(//section[@role="dialog"]//button)[last()]', timeout=30)
        sb.sleep(2)

    def get_months_container(self, sb):
        month_left_selector = f'[class="uitk-month uitk-month-double uitk-month-double-left"]'
        month_right_selector = f'[class="uitk-month uitk-month-double uitk-month-double-right"]'

        month_left = sb.cdp.find_element(month_left_selector)
        month_right = sb.cdp.find_element(month_right_selector)

        return month_left, month_right

    def standardize_data(self, data):
        return get_standard_data(data, self.params)
