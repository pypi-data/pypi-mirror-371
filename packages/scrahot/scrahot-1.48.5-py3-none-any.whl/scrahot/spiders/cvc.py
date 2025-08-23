import datetime
import json
import re
import time

import seleniumbase
from loguru import logger
# import pyautogui
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from scrahot.spiders.base import BaseSelenium
from scrahot.standard_json import get_standard_data_cvc
from scrahot.utils import XHRListener


class CvcSeleniumBase(BaseSelenium):
    def __init__(self):
        super().__init__('sb')
        self.name = 'cvc'
        self.params = {}
        self.requests_handle = XHRListener()

    def get_rooms(self, params):
        logger.debug(f'get_rooms: {params}')
        self.params = params

        website, region, location, start_day, start_month, start_year, end_day, end_month, end_year, adults, children, start_date, end_date = self.validate_input_data(
            params_required=['website', 'region', 'location', 'date_range', 'persons']
        )

        response = {
            "success": True,
            "search_criteria": params,
            "hotel": params.get('location'),
            "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
            'rooms': [],
        }
        current_url = None

        with seleniumbase.SB(uc=True, test=True, locale_code="en", ad_block=True, headed=True, window_size='1920,1080', maximize=True,
                             timeout_multiplier=3, save_screenshot=True) as sb:
            try:
                # https://seleniumbase.io/examples/cdp_mode/ReadMe/#cdp-mode-api-methods
                url = 'https://www.cvc.com.br/hotel'
                sb.activate_cdp_mode(url)
                sb.sleep(2.5)

                self.save_screenshot('cvc_home', driver=sb)

                # Handle banner modal
                try:
                    modal_close = sb.cdp.find_element('div[class*="html-close-button"]')
                    modal_close.click()
                    sb.sleep(1)
                except:
                    logger.debug("No modal found")

                # Enter Location
                # dest_field
                sb.cdp.click('input[type*="search"], input[placeholder*="Para onde você vai?"]')
                sb.sleep(0.5)
                input_field = sb.cdp.find_element('input[placeholder*="Para onde você vai?"], input[placeholder*="Ingresa una ciudad"]')
                input_field.send_keys(region)
                sb.sleep(1)
                # suggestion
                sb.cdp.click('div[role*="listbox"] li')
                sb.sleep(1)

                # self.save_screenshot('cvc_calendar1', driver=sb)

                # Enter Dates
                # date_field
                # sb.cdp.click('[id*="label-chui-2"]')
                # sb.sleep(1)


                # self.save_screenshot('cvc_calendar2', driver=sb)

                try:
                    prev_btn = sb.cdp.find_element('[data-testid*="prev-btn-datapicker"]')
                    next_btn = sb.cdp.find_element('[data-testid*="next-btn-datapicker"]')
                except Exception as e:
                    sb.cdp.click('[id*="label-chui-2"]')
                    sb.sleep(1)
                    prev_btn = sb.cdp.find_element('[data-testid*="prev-btn-datapicker"]')
                    next_btn = sb.cdp.find_element('[data-testid*="next-btn-datapicker"]')
                    logger.debug(f'Element not found or webpage not loaded in time: {e}')


                # calendar_container_selector = 'div[class*="css-1s9f2wz"]:not([class*="hidden"])'
                # calendar_container = sb.cdp.find_element(calendar_container_selector)
                month_left_selector = 'div[class*="css-13iw5lu"]:nth-of-type(1)'
                month_left = sb.cdp.find_element(month_left_selector)
                month_left.scroll_into_view()
                month_label = sb.cdp.find_element(f'{month_left_selector} [class*="css-7cuzsa"]')

                portuguese_to_english = {
                    'janeiro': 'January', 'fevereiro': 'February', 'março': 'March',
                    'abril': 'April', 'maio': 'May', 'junho': 'June',
                    'julho': 'July', 'agosto': 'August', 'setembro': 'September',
                    'outubro': 'October', 'novembro': 'November', 'dezembro': 'December'
                }

                # self.save_screenshot('cvc_calendar3', driver=sb)

                current_month = portuguese_to_english.get(month_label.text.split()[0].lower())
                current_year = int(month_label.text.split()[-1])
                target_month = start_date.strftime("%B")
                target_year = start_date.year

                while (current_month != target_month or current_year != target_year):
                    if (current_year < target_year) or (current_year == target_year and
                                                        datetime.datetime.strptime(current_month,
                                                                                   "%B").month < start_date.month):
                        next_btn.click()
                    else:
                        prev_btn.click()
                    sb.sleep(1)
                    month_label = sb.cdp.find_element(f'{month_left_selector} [class*="css-7cuzsa"]')
                    current_month = portuguese_to_english.get(month_label.text.split()[0].lower())
                    current_year = int(month_label.text.split()[-1])

                # Select dates
                day_class = 'chui-datepicker__element-day css-1se7wi1'
                month_calendar_selector = f'[class*="chui-datepicker__calendar-basic"]'
                month_calendar = sb.cdp.find_element(month_calendar_selector)
                month_left_cal_selector = f'{month_calendar_selector} section:nth-of-type(1)'
                month_right_cal_selector = f'{month_calendar_selector} section:nth-of-type(2)'
                month_left_cal = sb.cdp.find_element(month_left_cal_selector)
                month_right_cal = sb.cdp.find_element(month_right_cal_selector)

                start_day_selector = f'{month_left_cal_selector} button[class*="{day_class}"] label:not(:empty)'
                start_days = sb.cdp.find_elements(start_day_selector)
                for e in start_days:
                    if str(start_day) == e.text:
                        # e.flash(duration=0.5, color="EE4488")
                        # e.click()
                        e.mouse_click()
                        break
                sb.sleep(1)

                # self.save_screenshot('cvc', driver=sb)

                if end_date.month == start_date.month and end_date.year == start_year:
                    end_elements = sb.cdp.find_elements(
                        f'{month_left_cal_selector} button[class*="{day_class}"] label:not(:empty)')
                else:
                    end_elements = sb.cdp.find_elements(
                        f'{month_right_cal_selector} button[class*="{day_class}"] label:not(:empty)')

                # self.save_screenshot('inbewteen-dayselection', driver=sb)
                for e in end_elements:
                    if str(end_day) == e.text:
                        # e.flash(duration=0.5, color="EE4488")
                        # e.click()
                        e.mouse_click()
                        break
                sb.sleep(1)

                # self.save_screenshot('after-endday', driver=sb)
                sb.cdp.click('div[class*="css-xnqb19"] button')
                sb.sleep(1)

                # self.save_screenshot('guess', driver=sb)
                # Enter Guests
                # guest input
                sb.cdp.mouse_click('div[class*="css-mcnpgf"] input')
                sb.sleep(1)

                room_controls_selector = 'div[class*="css-n09wm4"]'
                room_controls = sb.cdp.find_elements('div[class*="css-n09wm4"]')
                adults_input = sb.cdp.find_element(f'{room_controls_selector}:nth-of-type(2) span[class*="chui-counter__textLabel"]')
                current_adults = int(adults_input.text)

                remove_btn = sb.cdp.find_element(f'{room_controls_selector}:nth-of-type(2) button[class*="css-1ikriy9"]:nth-of-type(1)')
                add_btn = sb.cdp.find_element(f'{room_controls_selector}:nth-of-type(2) button[class*="css-1ikriy9"]:nth-of-type(2)')

                while current_adults != adults:
                    if current_adults < adults:
                        add_btn.mouse_click()
                    else:
                        remove_btn.mouse_click()
                    sb.sleep(1)
                    adults_input = sb.cdp.find_element(f'{room_controls_selector}:nth-of-type(2) span[class*="chui-counter__textLabel"]')
                    current_adults = int(adults_input.text)

                if children > 0:
                    add_child_btn = sb.cdp.find_element(f'{room_controls_selector}:nth-of-type(3) button[class*="css-1ikriy9"]:nth-of-type(2)')
                    for _ in range(children):
                        add_child_btn.mouse_click()
                        sb.sleep(1)

                    children_ages = sb.cdp.find_element(f'{room_controls_selector}:nth-of-type(4) div[class*="css-1k68bbl"]')
                    for age_field in children_ages:
                        age_field.mouse_click()
                        sb.sleep(0.5)
                        age_option = sb.cdp.find_element('div[role*="listbox"] li:not(:empty):where(:contains("3"))')
                        age_option.mouse_click()
                        sb.sleep(0.5)

                # guest_done
                sb.cdp.click('button[class*="css-1jggfo3"]')
                sb.sleep(1)
                # self.save_screenshot('searching', driver=sb)
                # Search
                # search_btn
                sb.cdp.click('#form-hotel button[form="form-hotel"]')
                sb.sleep(3)
                # self.save_screenshot('before-selecting-room', driver=sb)
                # Find hotel
                hotel_cards = sb.cdp.select_all('div[class*="aut-hotel-item list"][id*="hotel-"]:not(:has(.uitk-text-negative-theme))')
                found = False
                for card in hotel_cards:
                    if location.lower() in card.text.lower():
                        card.scroll_into_view()
                        card.query_selector('button[class*="buttonDetail available"]').mouse_click()
                        sb.sleep(2)
                        found = True

                if not found:
                    # filter_input
                    sb.cdp.send_keys('div[class*="aut-filter-text"] div ul li span div div input', location)
                    sb.sleep(2)
                    hotel_cards = sb.cdp.select_all('div[class*="aut-hotel-item list"][id*="hotel-"]')
                    for card in hotel_cards:
                        if location.lower() in card.text.lower():
                            detail_btn = card.query_selector('button[class*="buttonDetail available"]')
                            detail_btn.click()
                            sb.sleep(2)
                            found = True
                            break

                if not found:
                    raise Exception(f"Hotel not found for location: {location}")

                while len(sb.cdp.get_tabs()) > 1:
                    sb.cdp.close_active_tab()
                    sb.cdp.switch_to_newest_tab()
                    sb.sleep(0.6)

                logger.debug(f"Tabs opened: {sb.cdp.get_tabs()}")

                current_url = None
                # current_url = sb.cdp.get_current_url()
                currency = 'BRL'
                response = {
                    "success": True,

                    "search_criteria": params,

                    "hotel": params.get('location'),
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
                }
                # self.save_screenshot('selecting-room', driver=sb)
                rooms = []
                while True:
                    # sb.cdp.scroll_down(1)
                    sb.sleep(0.5)
                    try:
                        all_rooms = sb.cdp.select_all('div[class="cvc-core-25"]')
                    except Exception as e:
                        logger.debug(f"Timeout: {e}")
                        availability_buttons = sb.cdp.select_all("[class*='roomsAvaliablesWrap']")
                        for button in availability_buttons:
                            if 'Não disponível' in button.text:
                                raise Exception(f"No rooms available for the selected dates")

                    for room in all_rooms:
                        room.scroll_into_view()
                        sb.sleep(0.5)

                        description = ''
                        buttons = room.query_selector_all('div.room-card__title__button > button')
                        button_info = buttons[1] if len(buttons) > 1 else None
                        if button_info:
                            button_info.mouse_click()

                            description = sb.cdp.find_element('div.MuiDialogContent-root > div:nth-child(2) span').text
                            sb.cdp.click('[data-testid="close-room-detail"]')
                        full_name = room.query_selector('div > div.room-card__title > div > h6').text.strip()
                        name = re.sub(r"^\d+x\s*", "", full_name)
                        # number = re.search(r'(\d+)x', full_name).group(1)
                        price = room.query_selector(
                                'p.MuiTypography-root.aut-price-total.MuiTypography-body2' # total price
                                # 'h3[class="MuiTypography-root aut-price-parcial MuiTypography-h3"]' #partial price
                                                    ).text
                        price = re.sub(r'[^\d.,]', '', price).replace('.', '').replace(',',
                                                                                       '.')  # Extract number from price text

                        room = {
                            "name":  name,
                            "beds": [description],
                            "price": price,
                        }
                        rooms.append(room)

                    button_right_rooms = sb.cdp.find_element('nav.css-1elq7vm li:nth-child(5) button')
                    is_disabled = button_right_rooms.get_attribute('disabled')
                    if is_disabled == '':
                        break
                    else:
                        button_right_rooms.scroll_into_view()
                        button_right_rooms.click()
                        sb.sleep(0.5)

                response['rooms'] = rooms
                response['rooms_found'] = rooms.__len__()
                response['currency_prices'] = currency
            except Exception as e:
                response['success'] = False
                response['error'] = f"{type(e).__name__}: {str(e)}"
                logger.debug(f"Error: {type(e).__name__}: {e}")


        #
        # if current_url:
        #     with seleniumbase.SB(uc=True, test=True, locale_code="en", ad_block=True, window_size='1920,1080', headed=True, ) as sb:
        #         sb.activate_cdp_mode(current_url)
        #         tab = sb.cdp.page
        #         self.requests_handle.listenXHR(tab)
        #
        #         sb.cdp.open(current_url)
        #         time.sleep(2)
        #         for i in range(10):
        #             sb.cdp.scroll_down(8)
        #
        #         filtered_requests = []
        #         loop = sb.cdp.get_event_loop()
        #         xhr_responses = loop.run_until_complete(self.requests_handle.receiveXHR(tab))
        #         for response in xhr_responses:
        #             logger.debug("*** ==> XHR Request URL <== ***")
        #             logger.debug(f'{response["url"]}')
        #             # is_base64 = response["is_base64"]
        #             # b64_data = "Base64 encoded data"
        #             # try:
        #             #     headers = ast.literal_eval(response["body"])["headers"]
        #             #     logger.debug("*** ==> XHR Response Headers <== ***")
        #             #     logger.debug(headers if not is_base64 else b64_data)
        #             # except Exception:
        #             #     response_body = response["body"]
        #             #     logger.debug("*** ==> XHR Response Body <== ***")
        #             #     logger.debug(response_body if not is_base64 else b64_data)
        #             if ('/hotel/detail/api/detail' in response["url"] or '/p/api/hotel/detail' in response["url"]) \
        #                     and response.get("body"):
        #                 filtered_requests.append(response)
        #
        #         logger.debug(f"requests found: {filtered_requests.__len__()} out of {len(xhr_responses)}")
        #
        #         data_found = False
        #         if filtered_requests.__len__() == 1:
        #             response = filtered_requests[0]
        #
        #             # Parse the request body as JSON
        #             body = json.loads(response["body"])
        #
        #             # if body is a list get the first element
        #             if isinstance(body, list):
        #                 body = body[0]
        #
        #             response = self.standardize_data(body)
        #
        #             data_found = True
        #             logger.debug(f"Request URL: {response['url']}")
        #
        #         if not data_found:
        #             self.save_screenshot(driver=sb)
        #             raise Exception(f"Data not found")
        #
        #         # Get rooms
        #         # room_cards = sb.cdp.select_all('div[class*="aut-room-card-container"]')
        #         # for room in room_cards:
        #         #     try:
        #         #         name = room.query_selector('div[class*="room-title"]').text
        #         #         description = room.query_selector('div[class*="room-description"]').text
        #         #         bed_types = list(set(re.findall(r'(\w+\s*bed)', description, re.I)))
        #         #         price = room.query_selector('div[class*="price"]').text
        #         #
        #         #         response['rooms'].append({
        #         #             'name': name,
        #         #             'beds': bed_types,
        #         #             'price': price
        #         #         })
        #         #     except Exception as e:
        #         #         continue
        # else:
        #     logger.debug(f"Tab not opened")

        return response

    def standardize_data(self, data):
        return get_standard_data_cvc(data, self.params)
#
# class CvcSelenium(BaseSelenium):
#
#     def __init__(self):
#         super().__init__()
#
#         self.name = 'cvc'
#
#         # Only request URLs containing "despegar" or "whatever" will now be captured
#         self.driver.scopes = [
#             '.*cvc.*',
#         ]
#
#         self.params = {}
#
#     def get_rooms(self, params):
#         logger.debug(f'get_rooms: {params}')
#         self.params = params
#
#         website, region, location, start_day, start_month, start_year, end_day, end_month, end_year, adults, children, start_date, end_date = self.validate_input_data(params_required=['website', 'region', 'location', 'date_range', 'persons'])
#
#         # self.driver.execute_cdp_cmd("Runtime.disable", {})
#
#         url = 'https://www.cvc.com.br/p/hotel'
#         self.driver.get(url)
#
#         self.random_wait()
#         # self.driver.execute_script(
#         #     f"""setTimeout(() => window.location.href="{url}", 100)""")
#         # self.driver.service.stop()
#         # self.driver.reconnect()
#
#         logger.debug(f'url: {url}')
#
#         def banner_modal():
#             try:
#                 for i in range(2):
#                     print("looking for modal", i)
#                     input_element = self.wait.until(
#                         EC.presence_of_element_located((By.XPATH, f"//div[contains(@class, 'html-close-button')]")))
#
#                     print("closing modal")
#                     input_element.click()
#                     # self.move_and_click(input_element)
#                     self.random_wait()
#             except:
#                 print("no modal found")
#                 pass
#
#         # *** Entering LOCATION ***
#         def location_part():
#
#             banner_modal()
#
#             print(f'\n\nentering location: {location}')
#             destination_form_field_xpath = (f"//*[contains(@id, 'motor-texto-origem') "
#                                             f"or contains(@placeholder, 'Para onde você vai?')]") # f"//input[contains(@placeholder, 'Para onde você vai?') or contains(@placeholder, 'Ingresa una ciudad')]"
#             try:
#                 print(f'waiting for: {destination_form_field_xpath}')
#                 # Wait for actions to complete
#                 # input_element = self.wait.until(EC.presence_of_element_located((By.XPATH, destination_form_field_xpath)))
#
#                 # input_element_parent = input_element.find_element(By.XPATH, "./..")
#
#                 print(f'waiting for to be clickable: {destination_form_field_xpath}')
#                 # input_element = self.wait.until(EC.element_to_be_clickable((By.XPATH, destination_form_field_xpath)))
#                 input_element = self.wait.until(EC.presence_of_element_located((By.XPATH, destination_form_field_xpath)))
#
#                 self.move_and_click(input_element)
#                 self.random_wait()
#
#                 # input_element = input_element.find_element(By.XPATH,
#                 #                                            f".//input[contains(@placeholder, 'Para onde você vai?') or contains(@placeholder, 'Ingresa una ciudad')]")
#                 input_xpath = ".//input[contains(@placeholder, 'Para onde você vai?') or contains(@placeholder, 'Ingresa una ciudad')]"
#                 print(f'waiting for input to be clickable: {input_xpath}')
#                 input_element = self.wait.until(EC.presence_of_element_located((By.XPATH, input_xpath)))
#
#                 # Check if input element is not disabled
#                 # def input_enabled(driver):
#                 #     element = driver.find_element(By.XPATH, destination_form_field_xpath)
#                 #     return element.get_attribute("disabled") is None
#                 #
#                 # self.wait.until(input_enabled, message=f'Input is disabled: {destination_form_field_xpath}')
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
#             print(f'input_element: {input_element}')
#             print(f'input_element: {input_element.text}')
#             # Send keys to the input element
#             # input_element.click()
#             # self.move_and_click(input_element)
#             # self.random_wait()
#
#             # input_for_sure = input_element.find_element(By.XPATH, "//input[contains(@placeholder, 'Para onde você vai?') or contains(@placeholder, 'Ingresa una ciudad')]")
#             # self.move_and_click(input_for_sure)
#             # print(f'input_for_sure: {input_for_sure}')
#
#             # self.driver.execute_script("arguments[0].removeAttribute('disabled');", input_element)
#             # # Set the value using JavaScript
#             # self.driver.execute_script("arguments[0].value = arguments[1];", input_element, location)
#             #
#             # # Trigger any events that are necessary for the application to recognize the change
#             # self.driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", input_element)
#
#             print(f'sending location: {location}')
#             # input_element.send_keys(location)
#             self.actions.move_to_element(input_element).click().send_keys(region).perform()
#
#             input_element_selection_xpath = (f"//div[contains(@role, 'listbox')]"
#                                              f"//li")
#             try:
#                 input_element_selection = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, input_element_selection_xpath)))
#             except:
#                 print(f'Element not found or webpage not loaded in time: {input_element_selection_xpath}')
#                 self.save_screenshot()
#                 self.random_wait()
#                 try:
#                     input_element_selection = self.wait.until(
#                         EC.presence_of_all_elements_located((By.XPATH, input_element_selection_xpath)))
#                 except:
#                     print(f'Element not found or webpage not loaded in time: {input_element_selection_xpath}')
#                     self.save_screenshot()
#                     raise Exception(f'Element not found or webpage not loaded in time: {input_element_selection_xpath}')
#
#             input_element_selection[0].click()
#             # self.move_and_click(input_element_selection[0])
#
#             self.random_wait()
#
#             # input_element = self.wait.until(EC.presence_of_element_located((By.XPATH, destination_form_field_xpath)))
#             #
#             # input_element.send_keys(Keys.ENTER)
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
#             logger.debug(f'\n\nentering date: {start_date} to {end_date}')
#
#             # navigation_controls_xpath = f"//button[contains(@data-testid, 'prev-btn-datapicker') or contains(@data-testid, 'next-btn-datapicker')]"
#             # navigation_controls = self.driver.find_elements(By.XPATH, navigation_controls_xpath)
#             # prev_button_month = navigation_controls[0]
#             # next_button_month = navigation_controls[1]
#             # prev_button_month_xpath = f"//*[contains(@role, 'button') and contains(@class, 'DayPickerNavigation_leftButton')]"
#             prev_button_month_xpath = f"//*[contains(@data-testid, 'prev-btn-datapicker')]"
#             # next_button_month_xpath = f"//*[contains(@role, 'button') and contains(@class, 'DayPickerNavigation_rightButton')]"
#             next_button_month_xpath = f"//*[contains(@data-testid, 'next-btn-datapicker')]"
#             prev_button_month = None
#             next_button_month = None
#             try:
#                 prev_button_month = self.driver.find_element(By.XPATH, prev_button_month_xpath)
#                 next_button_month = self.driver.find_element(By.XPATH, next_button_month_xpath)
#             except:
#                 date_button_data_xpath = f"//*[contains(@id, 'label-chui-2')]"
#                 logger.debug(f'preparing for: {date_button_data_xpath}')
#                 try:
#                     date_button = self.driver.find_element(By.XPATH, date_button_data_xpath)
#                     date_button.click()
#                 except:
#                     logger.debug(f'Element not found or webpage not loaded in time: {date_button_data_xpath}')
#                     self.save_screenshot()
#                 # self.move_and_click(date_button)
#
#             if not prev_button_month or not next_button_month:
#                 prev_button_month = self.driver.find_element(By.XPATH, prev_button_month_xpath)
#                 next_button_month = self.driver.find_element(By.XPATH, next_button_month_xpath)
#
#             self.random_wait()
#
#             calendar_container_path = "//div[contains(@class,'css-1s9f2wz') and not(contains(@class, 'hidden'))]"
#             calendar_container = self.driver.find_element(By.XPATH, calendar_container_path)
#             # print(f'calendar_container: {calendar_container.__len__()}')
#             months_header = calendar_container.find_element(By.XPATH, f".//*[contains(@class, 'css-ivsijq')]")
#             months_calendar = calendar_container.find_element(By.XPATH, f".//*[contains(@class, 'chui-datepicker__calendar-basic chui-datepicker__calendar-basic--sm css-132kuhp')]")
#             month_left = months_header.find_elements(By.XPATH, f".//div[contains(@class, 'css-13iw5lu')]")[0]
#             month_right = months_header.find_elements(By.XPATH, f".//div[contains(@class, 'css-13iw5lu')]")[1]
#
#             month_label_class = 'css-7cuzsa'
#             month_left_label = month_left.find_element(By.XPATH, f".//*[contains(@class, '{month_label_class}')]")
#             start_date_text = month_left_label.text
#             cal_start_month_name = start_date_text.split()[0]
#             portuguese_to_english = {
#                 'janeiro': 'January',
#                 'fevereiro': 'February',
#                 'março': 'March',
#                 'abril': 'April',
#                 'maio': 'May',
#                 'junho': 'June',
#                 'julho': 'July',
#                 'agosto': 'August',
#                 'setembro': 'September',
#                 'outubro': 'October',
#                 'novembro': 'November',
#                 'dezembro': 'December'
#             }
#             cal_start_month_name = portuguese_to_english.get(cal_start_month_name.lower(), cal_start_month_name.lower()).lower()
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
#                 self.random_wait()
#
#                 month_left = months_header.find_elements(By.XPATH, f".//div[contains(@class, 'css-13iw5lu')]")[0]
#                 month_right = months_header.find_elements(By.XPATH, f".//div[contains(@class, 'css-13iw5lu')]")[1]
#
#                 try:
#                     month_left_label = month_left.find_element(By.XPATH, f".//*[contains(@class, '{month_label_class}')]")
#                 except:
#                     print(f'Element not found or webpage not loaded in time: {month_label_class}')
#                     self.save_screenshot()
#                     raise Exception(f'Element not found or webpage not loaded in time: {month_label_class}')
#
#                 print(f"month_left_label: {month_left_label.text}")
#
#                 start_date_text = month_left_label.text
#
#                 try:
#                     self.random_wait()
#                     cal_start_month_name = start_date_text.split()[0]
#                     cal_start_month_name = [v for k,v in portuguese_to_english.items() if k in cal_start_month_name.lower()][0]
#                     # cal_start_month_name = portuguese_to_english.get(cal_start_month_name.lower(),
#                     #                                               cal_start_month_name.lower()).lower()
#                     cal_start_month_number = datetime.datetime.strptime(cal_start_month_name, "%B").month
#                     print(f"cal_start_month_name: {cal_start_month_name}")
#                     year = int(start_date_text.split()[-1])
#                     self.random_wait()
#                 except Exception as e:
#                     print(f'Element not found or webpage not loaded in time: {cal_start_month_name}', e)
#                     self.save_screenshot()
#                     raise Exception(f'Element not found or webpage not loaded in time: {cal_start_month_name}', e)
#
#             # try:
#             #     month_left = self.wait.until(EC.presence_of_element_located((By.XPATH, calendar_container_path)))[0]
#             #     month_right = self.wait.until(EC.presence_of_element_located((By.XPATH, calendar_container_path)))[1]
#             # except:
#             #     print(f'Element not found or webpage not loaded in time: {calendar_container_path}')
#             #     self.save_screenshot()
#             #     raise Exception(f'Element not found or webpage not loaded in time: {calendar_container_path}')
#
#             self.random_wait()
#
#             month_left = months_calendar.find_elements(By.XPATH, f".//section")[0]
#             month_right = months_calendar.find_elements(By.XPATH, f".//section")[1]
#
#             self.random_wait()
#
#             day_class_name = 'chui-datepicker__element-day css-1se7wi1'
#
#             # setting start date
#             if start_date.month == cal_start_month_number and start_year == year:
#                 # select the start day
#                 print(f'select the start_day: {start_day}')
#                 # month_left.find_element(By.XPATH, f"//*[text()='{start_day}']").click()
#                 try:
#                     day_button_selected = None
#
#                     while not day_button_selected:
#
#                         day_button = month_left.find_element(By.XPATH,
#                                                              f".//button[contains(@class, '{day_class_name}') and .//label[text()='{start_day}']]")
#                         print(f'start day_button: {day_button.text}')
#                         day_button.click()
#                         # self.move_and_click(day_button)
#                         self.random_wait()
#
#                         day_button_selected = month_left.find_element(By.XPATH,
#                                                                   f".//button[contains(@class, '{day_class_name}') and .//label[text()='{start_day}'] and contains(@data-active, 'true')]")
#                         print(f'day_button_selected: {day_button_selected.text}')
#                 except:
#                     print(f'Element not found or webpage not loaded in time: {start_day}')
#                     # if this gives error is because the date is already selected.
#
#             # setting end date
#
#             # if the end date is in the left month of the calendar
#             if end_month.lower() in cal_start_month_name.lower() and end_year == year:
#                 # select the end day
#                 print(f'select the end_day: {end_day}')
#                 try:
#                     day_button_selected = None
#                     while not day_button_selected:
#                         day_button = month_left.find_element(By.XPATH,
#                                                              f".//*[contains(@class, '{day_class_name}') and .//label[text()='{end_day}']]")
#                         print(f'end day_button: {day_button.text}')
#                         day_button.click()
#                         # self.move_and_click(day_button)
#                         self.random_wait()
#
#                         day_button_selected = month_left.find_element(By.XPATH,
#                                                                       f".//*[contains(@class, '{day_class_name}') and .//label[text()='{end_day}'] and contains(@data-active, 'true')]")
#                         print(f'day_button_selected: {day_button_selected.text}')
#
#                 except:
#                     print(f'Element not found or webpage not loaded in time: {end_day}')
#                     # if this gives error is because the date is already selected.
#
#             else:
#                 try:
#                     # we look in the right calendar month
#                     print(f'we look in the right calendar month')
#                     day_button = month_right.find_elements(By.XPATH,
#                                                            f".//button[contains(@class, '{day_class_name}') and .//label[text()='{end_day}']]")
#
#                     if day_button.__len__() > 1:
#                         day_button[1].click()
#                         # self.move_and_click(day_button[1])
#                         print(f'end2 day_button: {day_button[1].text}')
#                     else:
#                         day_button[0].click()
#                         # self.move_and_click(day_button[0])
#                         print(f'end2 day_button: {day_button[0].text}')
#                     self.random_wait()
#                 except:
#                     print(f'Element not found or webpage not loaded in time: {end_day}')
#                     # if this gives error is because the date is already selected.
#
#             calendar_done_button_xpath = f"//*[contains(@class, 'css-xnqb19')]//button"
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
#         # *** Entering GUESTS ***
#         def rooms_part():
#             print(f'\n\nentering guests: {adults} adults and {children} children')
#             room_picker_data_xpath = f"//*[contains(@class, 'css-mcnpgf')]//input"
#             # room_picker_data_xpath = f'//*[@id="form-hotel"]/div[2]/div/div[2]/div[2]/div/div/fieldset/div/div/input'
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
#             room_controls_xpath = f"//div[contains(@class, 'css-n09wm4')]"
#             try:
#                 room_controls = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, room_controls_xpath)))
#             except:
#                 print(f'Element not found or webpage not loaded in time: {room_controls_xpath}')
#                 self.save_screenshot()
#                 raise Exception(f'Element not found or webpage not loaded in time: {room_controls_xpath}')
#
#             # room_controls_footer_xpath = f"//div[contains(@class, 'distribution__container')]//*[contains(@class,'stepper__room__footer')]"
#             # room_controls_footer = self.driver.find_element(By.XPATH, room_controls_footer_xpath)
#
#             # remove_adults_xpath = f".//descendant::button[1]"
#             adults_input_xpath = f".//span[contains(@class,'chui-typography chui-counter__textLabel css-1oobp1g')]"
#             # adults_input = self.wait.until(EC.presence_of_element_located((By.XPATH, adults_input_xpath)))
#             adults_input = room_controls[1].find_element(By.XPATH, adults_input_xpath)
#
#             # increase_adults_xpath = f".//descendant::button[2]"
#             remove_adults_xpath = f".//button[contains(@class,'css-1ikriy9')]"
#             increase_adults_xpath = f".//button[contains(@class,'css-1ikriy9')]"
#             if adults and adults >= 1:
#                 current_adults = int(adults_input.text)
#                 while current_adults != adults:
#                     remove_adult_button = room_controls[1].find_elements(By.XPATH, remove_adults_xpath)[0]
#                     add_adult_button = room_controls[1].find_elements(By.XPATH, increase_adults_xpath)[1]
#
#                     if current_adults < adults:
#                         add_adult_button.click()
#                         # self.move_and_click(add_adult_button)
#                         self.random_wait()
#                     else:
#                         remove_adult_button.click()
#                         # self.move_and_click(remove_adult_button)
#                         self.random_wait()
#
#                     adults_input = WebDriverWait(room_controls[1], 10).until(EC.presence_of_element_located((By.XPATH, adults_input_xpath)))
#                     # adults_input = room_controls[0].find_element(By.XPATH, adults_input_xpath)
#                     current_adults = int(adults_input.text)
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
#                 increase_children_xpath = f".//button[contains(@class,'css-1ikriy9')]"
#                 # # add adult
#                 # add_adult_button = self.driver.find_element(By.XPATH, f"//*[@aria-describedby='adultCountLabel']")
#                 # add_adult_button.click()
#
#                 for i in range(children):
#                     add_children_button = room_controls[2].find_elements(By.XPATH, increase_children_xpath)[1]
#                     if add_children_button.is_enabled():
#                         print(f"add children {i}")
#                         add_children_button.click()
#                         # self.move_and_click(add_children_button)
#                         self.random_wait()
#                     else:
#                         print(f"add children {i} button not enabled")
#
#                 self.random_wait()
#
#                 try:
#
#                     room_controls = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, room_controls_xpath)))
#                     self.random_wait()
#                 except:
#                     print(f'Element not found or webpage not loaded in time: {room_controls_xpath}')
#                     self.save_screenshot()
#                     raise Exception(f'Element not found or webpage not loaded in time: {room_controls_xpath}')
#
#                 print(f"room_controls: {room_controls.__len__()}")
#
#                 children_ages_xpath = f".//div[contains(@class,'css-1k68bbl')]"
#                 children_ages = room_controls[3].find_elements(By.XPATH, children_ages_xpath)
#
#                 print(f"children_ages: {children_ages.__len__()}")
#
#                 for i in range(children_ages.__len__()):
#                     print(f"selecting age for child {i}")
#                     self.random_wait()
#                     children_ages[i].click()
#                     # self.move_and_click(children_ages[i])
#                     self.random_wait()
#                     list_box = self.driver.find_element(By.XPATH, f"//div[contains(@role, 'listbox')]"
#                                                        f"//li[contains(@role, 'option') and contains(text(), '3')]")
#                     list_box.click()
#                     # self.move_and_click(list_box)
#
#                     #Select(children_ages[i]).select_by_value("10")
#
#             guest_done_button_xpath = f"//button[contains(@class, 'css-1jggfo3')]"
#             try:
#                 done_button = self.driver.find_element(By.XPATH, guest_done_button_xpath)
#                 self.random_wait()
#             except:
#                 print(f'Element not found or webpage not loaded in time: {guest_done_button_xpath}')
#                 self.save_screenshot()
#                 raise Exception(f'Element not found or webpage not loaded in time: {guest_done_button_xpath}')
#
#             done_button.click()
#             # self.move_and_click(done_button)
#
#             self.random_wait()
#             # self.random_wait()
#
#         rooms_part()
#
#         # search_button_xpath = f"//*[@id='form-hotel']/div[2]/div/div[3]/button"
#         search_button_xpath = f"//*[@id='form-hotel']//button[@form='form-hotel']"
#         # search_button_xpath = f"//button[contains(@class, 'chui-button css-uhcw25') or contains(text(),'Buscar') or contains(text(), 'Buscar Hotéis')]"
#
#         try:
#             search_button = self.wait.until(EC.presence_of_element_located((By.XPATH, search_button_xpath)))
#             self.random_wait()
#         except:
#             print(f'Element not found or webpage not loaded in time: {search_button_xpath}')
#             self.save_screenshot()
#             raise Exception(f'Element not found or webpage not loaded in time: {search_button_xpath}')
#
#         # # Disable JavaScript execution
#         # self.driver.execute_cdp_cmd("Runtime.disable", {})
#
#         search_button.click()
#         # self.move_and_click(search_button)
#
#         self.random_wait()
#
#         # # Enable JavaScript execution
#         # self.driver.execute_cdp_cmd("Runtime.enable", {})
#
#         # self.driver.execute_script(f"window.open('_blank', 'Testing');")
#         # self.driver.switch_to.window(self.driver.window_handles[1])
#         # self.random_wait()
#         # self.driver.switch_to.window(self.driver.window_handles[0])
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
#         # close_stay_usa_xpath = f"//*[contains(text(), 'Continuar no Decolar Brasil')]"
#         # try:
#         #     self.random_wait()
#         #     close_modal = self.wait.until(EC.presence_of_element_located((By.XPATH, close_stay_usa_xpath)))
#         #     self.random_wait()
#         #     # close_modal.click()
#         #     self.move_and_click(close_modal)
#         #     self.random_wait()
#         # except:
#         #     print(f'Element not found or webpage not loaded in time: {close_stay_usa_xpath}')
#
#         # close_modal_xpath = f"//*[contains(@class, 'login-aggressive--button login-aggressive--button-close shifu-3-btn-ghost')]"
#         # try:
#         #     self.random_wait()
#         #     close_modal = self.wait.until(EC.presence_of_element_located((By.XPATH, close_modal_xpath)))
#         #     self.random_wait()
#         #     # close_modal.click()
#         #     self.move_and_click(close_modal)
#         #     self.random_wait()
#         # except:
#         #     print(f'Element not found or webpage not loaded in time: {close_modal_xpath}')
#
#         # select_currency_xpath = f"//select[.//option[@value='USD'] or .//option[@value='BRL']]"
#         # try:
#         #     self.random_wait()
#         #     select_currency = Select(self.wait.until(EC.presence_of_element_located((By.XPATH, select_currency_xpath))))
#         #     select_currency.select_by_value('USD')
#         #     self.random_wait()
#         # except:
#         #     print(f'Element not found or webpage not loaded in time: {select_currency_xpath}')
#         #     self.save_screenshot()
#         #     raise Exception(f'Element not found or webpage not loaded in time: {select_currency_xpath}')
#
#         # try:
#         #     # Wait for the div with the `infinitescroll` attribute to not have the `-eva-3-hide` class
#         #     self.wait.until(
#         #         EC.presence_of_element_located(
#         #             (By.XPATH, "//div[@infinitescroll and  not(contains(@class, '-eva-3-hide'))]"))
#         #     )
#         # except Exception:
#         #     print('Timed out waiting for the div with "infinitescroll" attribute to become visible.')
#         #     self.save_screenshot()
#
#         def look_for_hotel():
#             found = False
#             property_listing_result_xpath = f"//div[contains(@class,'aut-hotel-item list') and contains(@id, 'hotel-')]"
#             # property_listing_result_xpath = f"//*[@id='form-hotel']/div[2]/div/div[1]/div/div/div/div[2]/div/li[1]"
#             results_property = []
#             try:
#                 # Wait up to 10 seconds before throwing a TimeoutException unless it finds the element to return within 10 seconds
#                 results_property = self.wait.until(
#                     EC.presence_of_all_elements_located((By.XPATH, property_listing_result_xpath))
#                 )
#             except:
#                 print(f'Element not found or webpage not loaded in time: {property_listing_result_xpath}')
#                 self.save_screenshot()
#                 return found
#                 # raise Exception(f'Element not found or webpage not loaded in time: {property_listing_result_xpath}')
#
#             self.random_wait()
#
#             negative_theme_class = 'uitk-text-negative-theme'  # sin disponibilidad / we are sold out
#             property_class = 'uitk-spacing uitk-spacing-margin-blockstart-three'
#             # results_property = self.driver.find_element(By.XPATH,
#             #                                             f"//*[@data-stid='{property_listing_result_stid}']") \
#             #                               .find_elements(By.XPATH,
#             #                                              f".//div[@class='{property_class}']")
#
#             # data-test-id="price-summary" # we can look for this.
#
#             # pyautogui.hotkey("Ctrl", "Shift", "J")  # close dev tab tool
#
#
#             for i in range(results_property.__len__()):
#                 try:
#                     result_element = results_property[i]
#
#                     # print(f"title_element_text: {title_element.text}")
#                     found_elements = location.lower() in result_element.text.lower()
#
#                     if found_elements:
#                         print(f"found location: {location} in {result_element.text}")
#
#                         try:
#                             sold_out = result_element.find_element(By.XPATH,
#                                                                    f".//*[@class='{negative_theme_class}']")
#
#                             if sold_out:
#                                 print(f"Sold out")
#                                 continue
#                                 # yield item
#
#                         except NoSuchElementException:
#                             print("Not sold out.")
#
#                         if result_element.is_enabled():
#                             print(f"click room {i}")
#
#                             # Now, you can clear the request history
#                             del self.driver.requests
#
#                             result_element.location_once_scrolled_into_view
#                             self.save_screenshot()
#                             # result_element.click()
#
#                             self.random_wait()
#                             button_hotel = result_element.find_element(By.XPATH, ".//button[contains(@class, 'buttonDetail available')]")
#                             button_hotel.click()
#                             # self.move_and_click(button_hotel)
#                             self.random_wait()
#                             # ActionChains(self.driver).move_to_element(result_element).click(result_element).perform()
#
#                             # self.wait.until(EC.number_of_windows_to_be(2))
#                             #
#                             # # Switch to the new tab. It's usually the last tab in the window_handles list.
#                             # self.driver.switch_to.window(self.driver.window_handles[-1])
#
#                             # Store the original window handle for reference
#                             original_window_handle = self.driver.current_window_handle
#
#                             # Wait for a new window or tab to be opened
#                             self.wait.until(EC.new_window_is_opened([original_window_handle]))
#
#                             # Switch to the new window or tab, which should be the last in the list of window handles
#                             new_window_handle = [handle for handle in self.driver.window_handles if handle != original_window_handle][0]
#                             self.driver.switch_to.window(new_window_handle)
#
#                             found = True
#                             break
#                 except Exception as e:
#                     return look_for_hotel()
#
#             return found
#
#         found = look_for_hotel()
#
#         if not found:
#             print(f"not found first try {location}")
#             self.save_screenshot()
#
#             # input_filter_by_hotel_xpath = f"(//*[contains(@id, 'listMore')])[last()]/li/span/div/div/input"
#             input_filter_by_hotel_xpath = f"//*[contains(@class, 'aut-filter-text')]/div/ul/li/span/div/div/input"
#
#             try:
#                 self.random_wait()
#                 self.random_wait()
#                 self.random_wait()
#                 self.random_wait()
#                 # Wait up to 10 seconds before throwing a TimeoutException unless it finds the element to return within 10 seconds
#                 input_filter_by_hotel = self.wait.until(
#                     EC.presence_of_element_located((By.XPATH, input_filter_by_hotel_xpath))
#                 )
#                 input_filter_by_hotel.location_once_scrolled_into_view
#                 self.random_wait()
#                 self.actions.move_to_element(input_filter_by_hotel).click().send_keys(location).perform()
#             except:
#                 print(f'Element not found or webpage not loaded in time: {input_filter_by_hotel_xpath}')
#                 self.save_screenshot()
#                 raise Exception(f'Element not found or webpage not loaded in time: {input_filter_by_hotel_xpath}')
#
#             self.random_wait()
#             self.random_wait()
#             self.random_wait()
#             self.random_wait()
#
#             found = look_for_hotel()
#
#             if not found:
#                 print(f"not found second try {location}")
#                 self.save_screenshot()
#                 raise Exception(f"Data not found")
#
#         section_room_xpath = f"//*[contains(@class, 'aut-room-card-container')]"
#         try:
#             # Wait up to 10 seconds before throwing a TimeoutException unless it finds the element to return within 10 seconds
#             self.wait.until(EC.presence_of_element_located((By.XPATH, section_room_xpath)))
#             self.random_wait()
#         except:
#             print(f'Element not found or webpage not loaded in time: {section_room_xpath}')
#             self.save_screenshot()
#             raise Exception(f'Element not found or webpage not loaded in time: {section_room_xpath}')
#
#         # Get the json result using the proxy solution found
#
#         filtered_requests = []
#         for request in self.driver.requests:
#             if ('/hotel/detail/api/detail' in request.path or '/p/api/hotel/detail' in request.path) \
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
#         return get_standard_data_cvc(data, self.params)

