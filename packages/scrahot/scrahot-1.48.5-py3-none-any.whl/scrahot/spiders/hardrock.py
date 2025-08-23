import calendar
import datetime
import json

from loguru import logger
# import pyautogui
from selenium.common import NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire.utils import decode

from scrahot.spiders.base import BaseSelenium
from scrahot.standard_json import get_standard_data_cvc, get_standard_data_hardrock


class HardrockSelenium(BaseSelenium):

    def __init__(self):
        super().__init__()

        self.name = 'hardrock'

        # Only request URLs containing "despegar" or "whatever" will now be captured
        self.driver.scopes = [
            '.*hardrock.*',
        ]

        self.params = {}

    def get_rooms(self, params):
        logger.debug(f'get_rooms: {params}')
        self.params = params

        website, region, location, start_day, start_month, start_year, end_day, end_month, end_year, adults, children, start_date, end_date = self.validate_input_data(params_required=['website', 'location', 'date_range', 'persons'])
        location_mapping = {
            'Cancun'.lower(): '59391',
            'Guadalajara'.lower(): '1867',
            'Vallarta'.lower(): '59388',
            'Los Cabos'.lower(): '1350',
            'Riviera Maya'.lower(): '59660',
        }

        # self.driver.get('https://hotel.hardrock.com/')
        #
        # destinations_xpath = f"//option[contains(@data-group, 'North America')]"
        # try:
        #     destinations_options = self.wait.until(
        #         EC.presence_of_all_elements_located((By.XPATH, destinations_xpath)))
        #
        #     # Iterate through each option element
        #     for option in destinations_options:
        #         # Extract the text (location name) and vid_id attribute
        #         location_name = option.text.strip().lower()
        #         vid_id = option.get_attribute('vid_id')
        #
        #         # Add to the mapping if vid_id exists
        #         if vid_id:
        #             location_mapping[location_name] = vid_id
        #
        #     logger.debug("Location mapping:", location_mapping)
        #
        # except:
        #     print(f'Element not found or webpage not loaded in time: {destinations_xpath}')
        #     self.save_screenshot()
        #     raise Exception(f'Element not found or webpage not loaded in time: {destinations_xpath}')

        url = ('https://hotel.reservations.hardrock.com/'
               '?WT.mc_id=brand_bookingwidget'
               f'&adult={adults}'
               f'&arrive={start_date.strftime("%Y-%m-%d")}'
               f'&chain=13924'
               f'&child={children}'
               f'&currency=USD'
               f'&depart={end_date.strftime("%Y-%m-%d")}'
               f'&hotel={location_mapping.get(location.lower())}'
               f'&level=hotel&locale=en-US&productcurrency=USD&rooms=1')

        self.driver.get(url)

        self.random_wait()

        logger.debug(f'url: {url}')

        def banner_modal():
            try:
                for i in range(2):
                    print("looking for modal", i)
                    input_element = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, f"//div[contains(@class, 'html-close-button')]")))

                    print("closing modal")
                    input_element.click()
                    # self.move_and_click(input_element)
                    self.random_wait()
            except:
                print("no modal found")
                pass

        # *** Entering LOCATION ***
        def location_part():

            # banner_modal()

            logger.debug(f'\n\nentering location: {location}')
            destination_form_field_xpath = f"//*[contains(@id, 'locationFieldMultiEngineBookingWidgetWidget1448531')]"
            try:
                print(f'waiting for to be clickable: {destination_form_field_xpath}')
                # input_element = self.wait.until(EC.element_to_be_clickable((By.XPATH, destination_form_field_xpath)))
                input_element = self.wait.until(EC.presence_of_element_located((By.XPATH, destination_form_field_xpath)))

                self.move_and_click(input_element)
                self.random_wait()

                # input_element = input_element.find_element(By.XPATH,
                #                                            f".//input[contains(@placeholder, 'Para onde você vai?') or contains(@placeholder, 'Ingresa una ciudad')]")
                input_xpath = ".//input[contains(@placeholder, 'Para onde você vai?') or contains(@placeholder, 'Ingresa una ciudad')]"
                print(f'waiting for input to be clickable: {input_xpath}')
                input_element = self.wait.until(EC.presence_of_element_located((By.XPATH, input_xpath)))

            except:
                print(f'Element not found or webpage not loaded in time: {destination_form_field_xpath}')
                self.save_screenshot()
                raise Exception(f'Element not found or webpage not loaded in time: {destination_form_field_xpath}')


            logger.debug(f'sending location: {location}')
            # input_element.send_keys(location)
            Select(input_element).select_by_value(location)

            self.random_wait()

        # location_part()

        # *** Entering DATE ***
        def calendar_part():
            print(f'\n\nentering date: {start_date} to {end_date}')
            date_button_data_xpath = f"//*[contains(@id, 'label-chui-2')]"
            # date_button_data_xpath = f'//*[@id="form-hotel"]/div[2]/div/div[2]/div[1]/div/div/fieldset[1]/div/div/input'
            print(f'preparing for: {date_button_data_xpath}')

            try:
                # Find the button using its data-stid attribute and click it
                date_button = self.driver.find_element(By.XPATH, date_button_data_xpath)
                date_button.click()
            except:
                print(f'Element not found or webpage not loaded in time: {date_button_data_xpath}')
                self.save_screenshot()
            # self.move_and_click(date_button)

            self.random_wait()
            # navigation_controls_xpath = f"//button[contains(@data-testid, 'prev-btn-datapicker') or contains(@data-testid, 'next-btn-datapicker')]"
            # navigation_controls = self.driver.find_elements(By.XPATH, navigation_controls_xpath)
            # prev_button_month = navigation_controls[0]
            # next_button_month = navigation_controls[1]
            prev_button_month = self.driver.find_element(By.XPATH,
                                                         f"//*[contains(@data-testid, 'prev-btn-datapicker')]")
            next_button_month = self.driver.find_element(By.XPATH,
                                                         f"//*[contains(@data-testid, 'next-btn-datapicker')]")

            calendar_container_path = "//div[contains(@class,'css-1s9f2wz') and not(contains(@class, 'hidden'))]"
            calendar_container = self.driver.find_element(By.XPATH, calendar_container_path)
            # print(f'calendar_container: {calendar_container.__len__()}')
            months_header = calendar_container.find_element(By.XPATH, f".//*[contains(@class, 'css-ivsijq')]")
            months_calendar = calendar_container.find_element(By.XPATH, f".//*[contains(@class, 'chui-datepicker__calendar-basic chui-datepicker__calendar-basic--sm css-132kuhp')]")
            month_left = months_header.find_elements(By.XPATH, f".//div[contains(@class, 'css-13iw5lu')]")[0]
            month_right = months_header.find_elements(By.XPATH, f".//div[contains(@class, 'css-13iw5lu')]")[1]

            month_label_class = 'css-7cuzsa'
            month_left_label = month_left.find_element(By.XPATH, f".//*[contains(@class, '{month_label_class}')]")
            start_date_text = month_left_label.text
            cal_start_month_name = start_date_text.split()[0]
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

                month_left = months_header.find_elements(By.XPATH, f".//div[contains(@class, 'css-13iw5lu')]")[0]
                month_right = months_header.find_elements(By.XPATH, f".//div[contains(@class, 'css-13iw5lu')]")[1]

                try:
                    month_left_label = month_left.find_element(By.XPATH, f".//*[contains(@class, '{month_label_class}')]")
                except:
                    print(f'Element not found or webpage not loaded in time: {month_label_class}')
                    self.save_screenshot()
                    raise Exception(f'Element not found or webpage not loaded in time: {month_label_class}')

                print(f"month_left_label: {month_left_label.text}")

                start_date_text = month_left_label.text

                try:
                    self.random_wait()
                    cal_start_month_name = start_date_text.split()[0]
                    cal_start_month_name = [v for k,v in portuguese_to_english.items() if k in cal_start_month_name.lower()][0]
                    # cal_start_month_name = portuguese_to_english.get(cal_start_month_name.lower(),
                    #                                               cal_start_month_name.lower()).lower()
                    cal_start_month_number = datetime.datetime.strptime(cal_start_month_name, "%B").month
                    print(f"cal_start_month_name: {cal_start_month_name}")
                    year = int(start_date_text.split()[-1])
                    self.random_wait()
                except Exception as e:
                    print(f'Element not found or webpage not loaded in time: {cal_start_month_name}', e)
                    self.save_screenshot()
                    raise Exception(f'Element not found or webpage not loaded in time: {cal_start_month_name}', e)

            # try:
            #     month_left = self.wait.until(EC.presence_of_element_located((By.XPATH, calendar_container_path)))[0]
            #     month_right = self.wait.until(EC.presence_of_element_located((By.XPATH, calendar_container_path)))[1]
            # except:
            #     print(f'Element not found or webpage not loaded in time: {calendar_container_path}')
            #     self.save_screenshot()
            #     raise Exception(f'Element not found or webpage not loaded in time: {calendar_container_path}')

            self.random_wait()

            month_left = months_calendar.find_elements(By.XPATH, f".//section")[0]
            month_right = months_calendar.find_elements(By.XPATH, f".//section")[1]

            self.random_wait()

            day_class_name = 'chui-datepicker__element-day css-1se7wi1'

            # setting start date
            if start_date.month == cal_start_month_number and start_year == year:
                # select the start day
                print(f'select the start_day: {start_day}')
                # month_left.find_element(By.XPATH, f"//*[text()='{start_day}']").click()
                try:
                    day_button_selected = None

                    while not day_button_selected:

                        day_button = month_left.find_element(By.XPATH,
                                                             f".//button[contains(@class, '{day_class_name}') and .//label[text()='{start_day}']]")
                        print(f'start day_button: {day_button.text}')
                        day_button.click()
                        # self.move_and_click(day_button)
                        self.random_wait()

                        day_button_selected = month_left.find_element(By.XPATH,
                                                                  f".//button[contains(@class, '{day_class_name}') and .//label[text()='{start_day}'] and contains(@data-active, 'true')]")
                        print(f'day_button_selected: {day_button_selected.text}')
                except:
                    print(f'Element not found or webpage not loaded in time: {start_day}')
                    # if this gives error is because the date is already selected.

            # setting end date

            # if the end date is in the left month of the calendar
            if end_month.lower() in cal_start_month_name.lower() and end_year == year:
                # select the end day
                print(f'select the end_day: {end_day}')
                try:
                    day_button_selected = None
                    while not day_button_selected:
                        day_button = month_left.find_element(By.XPATH,
                                                             f".//*[contains(@class, '{day_class_name}') and .//label[text()='{end_day}']]")
                        print(f'end day_button: {day_button.text}')
                        day_button.click()
                        # self.move_and_click(day_button)
                        self.random_wait()

                        day_button_selected = month_left.find_element(By.XPATH,
                                                                      f".//*[contains(@class, '{day_class_name}') and .//label[text()='{end_day}'] and contains(@data-active, 'true')]")
                        print(f'day_button_selected: {day_button_selected.text}')

                except:
                    print(f'Element not found or webpage not loaded in time: {end_day}')
                    # if this gives error is because the date is already selected.

            else:
                try:
                    # we look in the right calendar month
                    print(f'we look in the right calendar month')
                    day_button = month_right.find_elements(By.XPATH,
                                                           f".//button[contains(@class, '{day_class_name}') and .//label[text()='{end_day}']]")

                    if day_button.__len__() > 1:
                        day_button[1].click()
                        # self.move_and_click(day_button[1])
                        print(f'end2 day_button: {day_button[1].text}')
                    else:
                        day_button[0].click()
                        # self.move_and_click(day_button[0])
                        print(f'end2 day_button: {day_button[0].text}')
                    self.random_wait()
                except:
                    print(f'Element not found or webpage not loaded in time: {end_day}')
                    # if this gives error is because the date is already selected.

            calendar_done_button_xpath = f"//*[contains(@class, 'css-xnqb19')]//button"
            try:
                calendar_done_button = self.driver.find_element(By.XPATH, calendar_done_button_xpath)
            except:
                print(f'Element not found or webpage not loaded in time: {calendar_done_button_xpath}')
                self.save_screenshot()
                raise Exception(f'Element not found or webpage not loaded in time: {calendar_done_button_xpath}')
            calendar_done_button.click()
            # self.move_and_click(calendar_done_button)
            self.random_wait()

        # calendar_part()

        # *** Entering GUESTS ***
        def rooms_part():
            print(f'\n\nentering guests: {adults} adults and {children} children')
            room_picker_data_xpath = f"//*[contains(@class, 'css-mcnpgf')]//input"
            # room_picker_data_xpath = f'//*[@id="form-hotel"]/div[2]/div/div[2]/div[2]/div/div/fieldset/div/div/input'
            try:
                button_room_picker = self.wait.until(EC.presence_of_element_located((By.XPATH, room_picker_data_xpath)))
            except:
                print(f'Element not found or webpage not loaded in time: {room_picker_data_xpath}')
                self.save_screenshot()
                raise Exception(f'Element not found or webpage not loaded in time: {room_picker_data_xpath}')

            button_room_picker.click()
            # self.move_and_click(button_room_picker)

            self.random_wait()

            room_controls_xpath = f"//div[contains(@class, 'css-n09wm4')]"
            try:
                room_controls = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, room_controls_xpath)))
            except:
                print(f'Element not found or webpage not loaded in time: {room_controls_xpath}')
                self.save_screenshot()
                raise Exception(f'Element not found or webpage not loaded in time: {room_controls_xpath}')

            # room_controls_footer_xpath = f"//div[contains(@class, 'distribution__container')]//*[contains(@class,'stepper__room__footer')]"
            # room_controls_footer = self.driver.find_element(By.XPATH, room_controls_footer_xpath)

            # remove_adults_xpath = f".//descendant::button[1]"
            adults_input_xpath = f".//span[contains(@class,'chui-typography chui-counter__textLabel css-1oobp1g')]"
            # adults_input = self.wait.until(EC.presence_of_element_located((By.XPATH, adults_input_xpath)))
            adults_input = room_controls[1].find_element(By.XPATH, adults_input_xpath)

            # increase_adults_xpath = f".//descendant::button[2]"
            remove_adults_xpath = f".//button[contains(@class,'css-1ikriy9')]"
            increase_adults_xpath = f".//button[contains(@class,'css-1ikriy9')]"
            if adults and adults >= 1:
                current_adults = int(adults_input.text)
                while current_adults != adults:
                    remove_adult_button = room_controls[1].find_elements(By.XPATH, remove_adults_xpath)[0]
                    add_adult_button = room_controls[1].find_elements(By.XPATH, increase_adults_xpath)[1]

                    if current_adults < adults:
                        add_adult_button.click()
                        # self.move_and_click(add_adult_button)
                        self.random_wait()
                    else:
                        remove_adult_button.click()
                        # self.move_and_click(remove_adult_button)
                        self.random_wait()

                    adults_input = WebDriverWait(room_controls[1], 10).until(EC.presence_of_element_located((By.XPATH, adults_input_xpath)))
                    # adults_input = room_controls[0].find_element(By.XPATH, adults_input_xpath)
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

                increase_children_xpath = f".//button[contains(@class,'css-1ikriy9')]"
                # # add adult
                # add_adult_button = self.driver.find_element(By.XPATH, f"//*[@aria-describedby='adultCountLabel']")
                # add_adult_button.click()

                for i in range(children):
                    add_children_button = room_controls[2].find_elements(By.XPATH, increase_children_xpath)[1]
                    if add_children_button.is_enabled():
                        print(f"add children {i}")
                        add_children_button.click()
                        # self.move_and_click(add_children_button)
                        self.random_wait()
                    else:
                        print(f"add children {i} button not enabled")

                self.random_wait()

                try:

                    room_controls = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, room_controls_xpath)))
                    self.random_wait()
                except:
                    print(f'Element not found or webpage not loaded in time: {room_controls_xpath}')
                    self.save_screenshot()
                    raise Exception(f'Element not found or webpage not loaded in time: {room_controls_xpath}')

                print(f"room_controls: {room_controls.__len__()}")

                children_ages_xpath = f".//div[contains(@class,'css-1k68bbl')]"
                children_ages = room_controls[3].find_elements(By.XPATH, children_ages_xpath)

                print(f"children_ages: {children_ages.__len__()}")

                for i in range(children_ages.__len__()):
                    print(f"selecting age for child {i}")
                    self.random_wait()
                    children_ages[i].click()
                    # self.move_and_click(children_ages[i])
                    self.random_wait()
                    list_box = self.driver.find_element(By.XPATH, f"//div[contains(@role, 'listbox')]"
                                                       f"//li[contains(@role, 'option') and contains(text(), '3')]")
                    list_box.click()
                    # self.move_and_click(list_box)

                    #Select(children_ages[i]).select_by_value("10")

            guest_done_button_xpath = f"//button[contains(@class, 'css-1jggfo3')]"
            try:
                done_button = self.driver.find_element(By.XPATH, guest_done_button_xpath)
                self.random_wait()
            except:
                print(f'Element not found or webpage not loaded in time: {guest_done_button_xpath}')
                self.save_screenshot()
                raise Exception(f'Element not found or webpage not loaded in time: {guest_done_button_xpath}')

            done_button.click()
            # self.move_and_click(done_button)

            self.random_wait()
            # self.random_wait()

        # rooms_part()

        def look_for_hotel():
            found = False
            property_listing_result_xpath = f"//div[contains(@class,'aut-hotel-item list') and contains(@id, 'hotel-')]"
            # property_listing_result_xpath = f"//*[@id='form-hotel']/div[2]/div/div[1]/div/div/div/div[2]/div/li[1]"
            results_property = []
            try:
                # Wait up to 10 seconds before throwing a TimeoutException unless it finds the element to return within 10 seconds
                results_property = self.wait.until(
                    EC.presence_of_all_elements_located((By.XPATH, property_listing_result_xpath))
                )
            except:
                print(f'Element not found or webpage not loaded in time: {property_listing_result_xpath}')
                self.save_screenshot()
                return found
                # raise Exception(f'Element not found or webpage not loaded in time: {property_listing_result_xpath}')

            self.random_wait()

            negative_theme_class = 'uitk-text-negative-theme'  # sin disponibilidad / we are sold out
            property_class = 'uitk-spacing uitk-spacing-margin-blockstart-three'
            # results_property = self.driver.find_element(By.XPATH,
            #                                             f"//*[@data-stid='{property_listing_result_stid}']") \
            #                               .find_elements(By.XPATH,
            #                                              f".//div[@class='{property_class}']")

            # data-test-id="price-summary" # we can look for this.

            # pyautogui.hotkey("Ctrl", "Shift", "J")  # close dev tab tool


            for i in range(results_property.__len__()):
                try:
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
                            # result_element.click()

                            self.random_wait()
                            button_hotel = result_element.find_element(By.XPATH, ".//button[contains(@class, 'buttonDetail available')]")
                            button_hotel.click()
                            # self.move_and_click(button_hotel)
                            self.random_wait()
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
                except Exception as e:
                    return look_for_hotel()

            return found

        # found = look_for_hotel()

        section_room_xpath = f"//*[contains(@class, 'thumb-cards_products')]"
        try:
            # Wait up to 10 seconds before throwing a TimeoutException unless it finds the element to return within 10 seconds
            self.wait.until(EC.presence_of_element_located((By.XPATH, section_room_xpath)))
            self.random_wait()
        except:
            print(f'Element not found or webpage not loaded in time: {section_room_xpath}')
            self.save_screenshot()
            raise Exception(f'Element not found or webpage not loaded in time: {section_room_xpath}')

        filtered_requests = []
        for request in self.driver.requests:
            if '/gw/product/v1/getProductAvailability' in request.path and request.response.body:
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
        return get_standard_data_hardrock(data, self.params)
