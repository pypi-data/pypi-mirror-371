import datetime
import json

from loguru import logger
from selenium.common import NoSuchElementException
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select

from scrahot.spiders.base import BaseSelenium
from scrahot.standard_json import get_standard_data_second


class DespegarSelenium(BaseSelenium):

    def __init__(self):
        super().__init__()

        self.name = 'despegar'

        # Only request URLs containing "decolar" or "whatever" will now be captured
        self.driver.scopes = [
            '.*despegar.*',
        ]

        self.params = {}

    def get_rooms(self, params):
        logger.debug(f'get_rooms: {params}')
        self.params = params

        website, region, location, start_day, start_month, start_year, end_day, end_month, end_year, adults, children, start_date, end_date = self.validate_input_data()

        url = 'https://www.us.despegar.com/hotels/'
        self.driver.get(url)

        logger.debug(f'url: {url}')

        self.driver.implicitly_wait(30)

        def close_login_incentive():
            logger.debug(f'close_login_incentive')
            # close the login incentive
            close_login_incentive_xpath = f"//div[contains(@class, 'login-incentive--button-close')]"
            try:
                close_login_incentive = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, close_login_incentive_xpath)))
                coords = close_login_incentive.location_once_scrolled_into_view
                close_login_incentive.click()
            except:
                logger.debug(f'Element not found or webpage not loaded in time: {close_login_incentive_xpath}')

        close_login_incentive()

        # *** Entering LOCATION ***
        def location_part():
            destination_form_field_xpath = f"//input[contains(@placeholder, 'Ingresa una ciudad') or contains(@placeholder, 'Destino')" \
                                           f" or contains(@placeholder, 'Type a city') or contains(@placeholder, 'Destination')]"
            try:
                print(f'waiting for: {destination_form_field_xpath}')
                # Wait for actions to complete
                input_element = self.wait.until(EC.presence_of_element_located((By.XPATH, destination_form_field_xpath)))
            except:
                logger.debug(f'Element not found or webpage not loaded in time: {destination_form_field_xpath}')
                self.save_screenshot()
                raise Exception(f'Element not found or webpage not loaded in time: {destination_form_field_xpath}')

            logger.debug(f'entering keys for: {destination_form_field_xpath}')

            logger.debug(f'waiting to be clickable: {destination_form_field_xpath}')
            # Use JavaScript to change the autocomplete attribute to 'on'

            logger.debug(f'input_element: {input_element.text}')
            # Send keys to the input element
            # input_element.click()
            self.move_and_click(input_element)
            self.random_wait()
            input_element.send_keys(location)

            self.random_wait()

            input_element_selection_xpath = (f"//*[contains(@class, 'ac-wrapper') and contains(@class, '-show')]"
                                             f"//*[contains(@class, 'ac-container')]//li")

            input_element_selection = self.wait_for_all_elements(input_element_selection_xpath)
            # input_element_selection[0].click()
            self.move_and_click(input_element_selection[0])

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
            date_button_data_xpath = f"//*[contains(@placeholder, 'Entrada') or contains(@placeholder, 'Check in')]"
            logger.debug(f'preparing for: {date_button_data_xpath}')

            # Find the button using its data-stid attribute and click it
            date_button = self.driver.find_element(By.XPATH, date_button_data_xpath)

            # date_button.click()
            self.move_and_click(date_button)

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

            # iterate to the correct month
            while not (start_year == year and start_date.month == cal_start_month_number):
                # iterate to the next month or previous month
                if start_year < year and start_date.month < cal_start_month_number:
                    # prev_button_month.click()
                    self.move_and_click(prev_button_month)
                elif start_year > year or start_date.month > cal_start_month_number:
                    # next_button_month.click()
                    self.move_and_click(next_button_month)

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
                cal_start_month_name = spanish_to_english.get(cal_start_month_name.lower(),
                                                              cal_start_month_name.lower()).lower()
                cal_start_month_number = datetime.datetime.strptime(cal_start_month_name, "%B").month
                year = int(start_date_text.split()[-1])

            # setting start date
            logger.debug(f'selecting start date: {start_date}')
            if start_date.month == cal_start_month_number and start_year == year:
                # select the start day
                # month_left.find_element(By.XPATH, f"//*[text()='{start_day}']").click()
                start_day_xpath = f".//*[contains(@class, 'sbox5-monthgrid-datenumber-number') and text()='{start_day}']"
                day_button = month_left.find_element(By.XPATH, start_day_xpath)
                # day_button.click()
                self.move_and_click(day_button)
                self.random_wait()

            # setting end date

            month_left = self.driver.find_elements(By.XPATH, calendar_container_path)[0]
            month_right = self.driver.find_elements(By.XPATH, calendar_container_path)[1]

            # if the end date is in the left month of the calendar
            logger.debug(f'selecting end date: {end_date}')
            if end_month.lower() in cal_start_month_name.lower() and end_year == year:
                # select the end day
                end_day_xpath =  f".//*[contains(@class, 'sbox5-monthgrid-datenumber-number') and text()='{end_day}']"
                try:
                    day_button = month_left.find_element(By.XPATH, end_day_xpath)

                    # day_button.click()
                    self.move_and_click(day_button)
                    self.random_wait()
                except:
                    print(f'Element not found or webpage not loaded in time: {end_day}')
                    self.save_screenshot()
                    raise Exception(f'Element not found or webpage not loaded in time: {end_day_xpath}')
                    # if this gives error is because the date is already selected.

            else:
                end_day_xpath = f".//*[contains(@class, 'sbox5-monthgrid-datenumber-number') and text()='{end_day}']"
                try:
                    # we look in the right calendar month
                    day_button = month_right.find_elements(By.XPATH, end_day_xpath)

                    if day_button.__len__() > 1:
                        # day_button[1].click()
                        self.move_and_click(day_button[1])
                    else:
                        # day_button[0].click()
                        self.move_and_click(day_button[0])
                    self.random_wait()
                except:
                    print(f'Element not found or webpage not loaded in time: {end_day}')
                    self.save_screenshot()
                    raise Exception(f'Element not found or webpage not loaded in time: {end_day_xpath}')
                    # if this gives error is because the date is already selected.

            logger.debug(f'clicking done button')
            calendar_done_button_xpath = f"//*[contains(@class, 'calendar-footer')]//button[contains(., 'Apply')]"
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
            logger.debug(f'rooms_part')
            room_picker_data_xpath = f"//*[contains(@class, 'sbox5-3-first-input-wrapper') or contains(@class, 'sbox5-3-second-input-wrapper')]"
            try:
                button_room_picker = self.wait.until(EC.presence_of_element_located((By.XPATH, room_picker_data_xpath)))
            except:
                print(f'Element not found or webpage not loaded in time: {room_picker_data_xpath}')
                self.save_screenshot()
                raise Exception(f'Element not found or webpage not loaded in time: {room_picker_data_xpath}')

            # button_room_picker.click()
            self.move_and_click(button_room_picker)

            logger.debug(f'button_room_picker clicked')

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
                        # add_adult_button.click()
                        self.move_and_click(add_adult_button)
                        self.random_wait()
                    else:
                        # remove_adult_button.click()
                        self.move_and_click(remove_adult_button)
                        self.random_wait()

                    adults_input = self.wait.until(EC.presence_of_element_located((By.XPATH, adults_input_xpath)))
                    current_adults = int(adults_input.get_attribute("value"))

            if children and children > 0:

                increase_children_xpath = f".//button[contains(@class,'steppers-icon-right')]"
                # # add adult
                # add_adult_button = self.driver.find_element(By.XPATH, f"//*[@aria-describedby='adultCountLabel']")
                # add_adult_button.click()

                for i in range(children):
                    add_children_button = room_controls[1].find_element(By.XPATH, increase_children_xpath)
                    if add_children_button.is_enabled():
                        logger.debug(f"add children {i}")
                        # add_children_button.click()
                        self.move_and_click(add_children_button)
                        self.random_wait()

                children_ages_xpath = f"//div[@class='stepper__distribution_container']//select[contains(@class,'select')]"
                children_ages = self.driver.find_elements(By.XPATH, children_ages_xpath)

                for i in range(children_ages.__len__()):
                    Select(children_ages[i]).select_by_value("10")

            guest_done_button_xpath = f".//*[contains(@class, '-primary') or contains(text(), 'Aplicar')]"
            self.wait_and_click_element(guest_done_button_xpath)

            self.random_wait()

        rooms_part()

        search_button_xpath = (f"//*[contains(@class, 'sbox5-box-content')]"
                               f"//*[contains(text(),'Buscar') or contains(text(), 'Search')]")

        search_button = self.wait_and_click_element(search_button_xpath)

        self.random_wait()
        self.random_wait()
        self.random_wait()

        self.driver.refresh()

        close_stay_usa_xpath = f"//*[contains(text(), 'Stay in Despegar USA') or contains(text(), 'Seguir en Despegar de USA')]"
        close_modal = self.wait_and_click_element(close_stay_usa_xpath, raise_exception=False)

        property_listing_result_xpath = f"//*[contains(@class,'results-cluster-container') and not(contains(@class,'results-banner-inner'))]"
        results_property = self.wait_for_all_elements(property_listing_result_xpath)
        self.random_wait()

        negative_theme_class = 'uitk-text-negative-theme'  # sin disponibilidad / we are sold out
        property_class = 'uitk-spacing uitk-spacing-margin-blockstart-three'
        # results_property = self.driver.find_element(By.XPATH,
        #                                             f"//*[@data-stid='{property_listing_result_stid}']") \
        #                               .find_elements(By.XPATH,
        #                                              f".//div[@class='{property_class}']")

        # data-test-id="price-summary" # we can look for this.

        self.save_screenshot()

        found = False
        for i in range(results_property.__len__()):
            result_element = results_property[i]

            # print(f"title_element_text: {title_element.text}")
            found_elements = location.lower() in result_element.text.lower()

            if found_elements:
                logger.debug(f"found location: {location} in {result_element.text}")

                try:
                    sold_out = result_element.find_element(By.XPATH,
                                                           f".//*[@class='{negative_theme_class}']")

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

                    self.save_screenshot('before_scroll')

                    self.random_wait()
                    coord = result_element.location_once_scrolled_into_view
                    self.random_wait()

                    tooltips_xpath = "//*[contains(@id, 'close-menu-wrong-country')]"
                    try:
                        tooltips = self.driver.find_elements(By.XPATH, tooltips_xpath)
                        for tooltip in tooltips:
                            self.random_wait()
                            tooltip.click()
                    except:
                        logger.debug(f'Element not found or webpage not loaded in time: {tooltips_xpath}')
                        self.save_screenshot()

                    # Check we don't have other windows open already
                    assert len(self.driver.window_handles) == 1, 'We should only have one window open at this point'

                    result_element.click()

                    # see_details_xpath = ".//*[contains(text(), 'See details')]"
                    # self.save_element_screenshot(result_element, 'seedetails')
                    # try:
                    #     # Wait up to 10 seconds before throwing a TimeoutException unless it finds the element to return within 10 seconds
                    #     results_property = result_element.find_element(By.XPATH, see_details_xpath)
                    #     self.random_wait()
                    #     results_property.click()
                    # except:
                    #     logger.debug(f'Element not found or webpage not loaded in time: {see_details_xpath}')
                    #     self.save_screenshot()
                    #     raise Exception(
                    #         f'Element not found or webpage not loaded in time: {see_details_xpath}')

                    # Store the original window handle for reference
                    original_window_handle = self.driver.current_window_handle

                    self.save_screenshot('after_scroll')

                    # Wait for a new window or tab to be opened
                    self.wait.until(EC.new_window_is_opened([original_window_handle]))

                    self.save_screenshot('before_switch_window1')

                    # Switch to the new window or tab, which should be the last in the list of window handles
                    new_window_handle = \
                    [handle for handle in self.driver.window_handles if handle != original_window_handle][0]
                    self.driver.switch_to.window(new_window_handle)
                    self.random_wait()
                    self.driver.refresh()


                    self.save_screenshot('after_switch_window')

                    self.random_wait()

                    found = True
                    break

        self.random_wait()

        if not found:
            logger.debug(f"not found {location}")
            self.save_screenshot()
            raise Exception(f"not found {location}")

        section_room_xpath = f"//*[contains(@class, 'rooms-container')]"
        try:
            # Wait up to 10 seconds before throwing a TimeoutException unless it finds the element to return within 10 seconds
            self.wait.until(EC.presence_of_element_located((By.XPATH, section_room_xpath)))
        except:
            logger.debug(f'Element not found or webpage not loaded in time: {section_room_xpath}')
            self.save_screenshot()
            raise Exception(f'Element not found or webpage not loaded in time: {section_room_xpath}')

        filtered_requests = []
        for request in self.driver.requests:
            # print(request)
            # for name, value in request.headers.items():
            #     print(f'\t{name}: {value}')
            if '/s-accommodations/api/accommodations/availability/rooms' in request.path \
                    and request.response.body:
                filtered_requests.append(request)

        logger.debug(f"requests found: {filtered_requests.__len__()} out of {self.driver.requests.__len__()}")

        data_found = False
        if filtered_requests.__len__() >= 1:
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