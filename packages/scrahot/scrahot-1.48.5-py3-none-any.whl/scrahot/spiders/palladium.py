import datetime
import json

from loguru import logger
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait


from scrahot.spiders.base import BaseSelenium
from scrahot.standard_json import get_standard_data_cvc, get_standard_data_palladium


class PalladiumSelenium(BaseSelenium):

    def __init__(self):
        super().__init__()

        self.name = 'palladium'

        # Only request URLs containing "despegar" or "whatever" will now be captured
        self.driver.scopes = [
            '.*palladium.*',
            '.*palladiumhotelgroup.*',
        ]

        self.params = {}

    def get_rooms(self, params):
        logger.debug(f'get_rooms: {params}')
        self.params = params

        website, region, location, start_day, start_month, start_year, end_day, end_month, end_year, adults, children, start_date, end_date = self.validate_input_data(params_required=['website', 'region', 'location', 'date_range', 'persons'])

        url = f'https://www.palladiumhotelgroup.com/en/hoteles'

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
            destination_form_field_xpath = f"//*[contains(@class, 'tab-content y_finderContainer-home')]//*[contains(@class, 'destino')]" # f"//input[contains(@placeholder, 'Para onde você vai?') or contains(@placeholder, 'Ingresa una ciudad')]"
            try:
                logger.debug(f'waiting for: {destination_form_field_xpath}')

                logger.debug(f'waiting for to be clickable: {destination_form_field_xpath}')
                input_element = self.wait.until(EC.presence_of_element_located((By.XPATH, destination_form_field_xpath)))

                self.move_and_click(input_element)
                self.random_wait()

            except:
                print(f'Element not found or webpage not loaded in time: {destination_form_field_xpath}')
                self.save_screenshot()
                raise Exception(f'Element not found or webpage not loaded in time: {destination_form_field_xpath}')

            print(f'entering keys for: {destination_form_field_xpath}')

            print(f'waiting to be clickable: {destination_form_field_xpath}')
            # Use JavaScript to change the autocomplete attribute to 'on'

            print(f'sending location: {location}')

            destination_form_field_xpath = f"//input[contains(@id, 'filtrar')]" # f"//input[contains(@placeholder, 'Para onde você vai?') or contains(@placeholder, 'Ingresa una ciudad')]"
            try:
                logger.debug(f'waiting for: {destination_form_field_xpath}')

                logger.debug(f'waiting for to be clickable: {destination_form_field_xpath}')
                input_element = self.wait.until(EC.presence_of_element_located((By.XPATH, destination_form_field_xpath)))
                self.random_wait()

            except:
                print(f'Element not found or webpage not loaded in time: {destination_form_field_xpath}')
                self.save_screenshot()
                raise Exception(f'Element not found or webpage not loaded in time: {destination_form_field_xpath}')
            # input_element.send_keys(location)
            self.actions.move_to_element(input_element).click().send_keys(location).perform()

            input_element_selection_xpath = (f"//*[contains(@id, 'pais-hoteles-mexico')]"
                                             f"//*[contains(@style,'display: block;') and contains(@id, 'destino-predictive')]")
            try:
                input_element_selection = self.wait.until(
                    EC.presence_of_all_elements_located((By.XPATH, input_element_selection_xpath)))
            except:
                print(f'Element not found or webpage not loaded in time: {input_element_selection_xpath}')
                self.save_screenshot()
                self.random_wait()
                try:
                    input_element_selection = self.wait.until(
                        EC.presence_of_all_elements_located((By.XPATH, input_element_selection_xpath)))
                except:
                    print(f'Element not found or webpage not loaded in time: {input_element_selection_xpath}')
                    self.save_screenshot()
                    raise Exception(f'Element not found or webpage not loaded in time: {input_element_selection_xpath}')

            input_element_selection[0].click()
            # self.move_and_click(input_element_selection[0])

            self.random_wait()

            # input_element = self.wait.until(EC.presence_of_element_located((By.XPATH, destination_form_field_xpath)))
            #
            # input_element.send_keys(Keys.ENTER)

            # Simulate typing some words
            # self.driver.switch_to.active_element.send_keys(location)
            # # Simulate hitting the Enter key
            # self.driver.switch_to.active_element.send_keys(Keys.ENTER)

            self.random_wait()

        location_part()

        # *** Entering DATE ***
        def calendar_part():
            print(f'\n\nentering date: {start_date} to {end_date}')
            date_button_data_xpath = f"//*[contains(@class,'dateRangeSummoner')]"
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
            # //*[contains(@class,'show-calendar') and contains(@style, 'display: block;')]//*[contains(@class,'calendar right')]//*[contains(@class, 'arrow-next')]

            calendar_container_path = "//*[contains(@class,'show-calendar') and contains(@style, 'display: block;')]"
            calendar_container = self.driver.find_element(By.XPATH, calendar_container_path)
            # print(f'calendar_container: {calendar_container.__len__()}')
            # months_header = calendar_container.find_element(By.XPATH, f".//*[contains(@class, 'css-ivsijq')]")
            # months_calendar = calendar_container.find_element(By.XPATH, f".//*[contains(@class, 'chui-datepicker__calendar-basic chui-datepicker__calendar-basic--sm css-132kuhp')]")
            month_left_xpath = f"//*[contains(@class,'show-calendar') and contains(@style, 'display: block;')]//*[contains(@class,'calendar left')]"
            month_right_xpath = f"//*[contains(@class,'show-calendar') and contains(@style, 'display: block;')]//*[contains(@class,'calendar right')]"
            month_left = self.driver.find_element(By.XPATH, month_left_xpath)
            month_right = self.driver.find_element(By.XPATH, month_right_xpath)

            month_label_class = 'month'
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
                'diciembre': 'December',

                'january': 'January',
                'february': 'February',
                'march': 'March',
                'april': 'April',
                'may': 'May',
                'june': 'June',
                'july': 'July',
                'august': 'August',
                'september': 'September',
                'october': 'October',
                'november': 'November',
                'december': 'December'
            }
            cal_start_month_name = spanish_to_english.get(cal_start_month_name.lower(), cal_start_month_name.lower()).lower()
            # Convert month name to month number using datetime module
            cal_start_month_number = datetime.datetime.strptime(cal_start_month_name, "%B").month
            year = int(start_date_text.split()[-1])

            # iterate to the correct month
            while not (start_year == year and start_date.month == cal_start_month_number):
                # iterate to the next month or previous month
                if start_year < year and start_date.month < cal_start_month_number:
                    prev_button_month = self.driver.find_element(By.XPATH,
                                                                 f"//*[contains(@class,'show-calendar') and contains(@style, 'display: block;')]//*[contains(@class,'calendar left')]//*[contains(@class, 'arrow-prev')]")
                    prev_button_month.click()
                    # self.move_and_click(prev_button_month)
                elif start_year > year or start_date.month > cal_start_month_number:
                    next_button_month = self.driver.find_element(By.XPATH,
                                                                 f"//*[contains(@class,'show-calendar') and contains(@style, 'display: block;')]//*[contains(@class,'calendar right')]//*[contains(@class, 'arrow-next')]")
                    next_button_month.click()
                    # self.move_and_click(next_button_month)
                self.random_wait()

                month_left = self.driver.find_element(By.XPATH, month_left_xpath)
                month_right = self.driver.find_element(By.XPATH, month_right_xpath)

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
                    cal_start_month_name = [v for k,v in spanish_to_english.items() if k in cal_start_month_name.lower()][0]
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

            month_left = self.driver.find_element(By.XPATH, month_left_xpath)
            month_right = self.driver.find_element(By.XPATH, month_right_xpath)

            self.random_wait()

            day_class_name = 'available'

            # setting start date
            if start_date.month == cal_start_month_number and start_year == year:
                # select the start day
                print(f'select the start_day: {start_day}')
                # month_left.find_element(By.XPATH, f"//*[text()='{start_day}']").click()
                try:
                    day_button_selected = None

                    while not day_button_selected:

                        day_button = month_left.find_element(By.XPATH,
                                                             f".//*[contains(@class, '{day_class_name}') and text()='{start_day}']")
                        print(f'start day_button: {day_button.text}')
                        day_button.click()
                        # self.move_and_click(day_button)
                        self.random_wait()

                        day_button_selected = month_left.find_element(By.XPATH,
                                                                  f".//*[contains(@class, '{day_class_name}') and text()='{start_day}']")
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
                                                             f".//*[contains(@class, '{day_class_name}') and text()='{end_day}']")
                        print(f'end day_button: {day_button.text}')
                        day_button.click()
                        # self.move_and_click(day_button)
                        self.random_wait()

                        day_button_selected = month_left.find_element(By.XPATH,
                                                                      f".//*[contains(@class, '{day_class_name}') and text()='{end_day}']")
                        print(f'day_button_selected: {day_button_selected.text}')

                except:
                    print(f'Element not found or webpage not loaded in time: {end_day}')
                    # if this gives error is because the date is already selected.

            else:
                try:
                    # we look in the right calendar month
                    print(f'we look in the right calendar month')
                    day_button = month_right.find_elements(By.XPATH,
                                                           f".//*[contains(@class, '{day_class_name}') and text()='{end_day}']")

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

            # calendar_done_button_xpath = f"//*[contains(@class, 'css-xnqb19')]//button"
            # try:
            #     calendar_done_button = self.driver.find_element(By.XPATH, calendar_done_button_xpath)
            # except:
            #     print(f'Element not found or webpage not loaded in time: {calendar_done_button_xpath}')
            #     self.save_screenshot()
            #     raise Exception(f'Element not found or webpage not loaded in time: {calendar_done_button_xpath}')
            # calendar_done_button.click()
            # # self.move_and_click(calendar_done_button)
            # self.random_wait()

        calendar_part()

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

        # search_button_xpath = f"//*[@id='form-hotel']/div[2]/div/div[3]/button"
        search_button_xpath = f"//*[contains(@class,'buscador__btn-reserva buscador__btn-reserva--validations-hotel')]"
        # search_button_xpath = f"//button[contains(@class, 'chui-button css-uhcw25') or contains(text(),'Buscar') or contains(text(), 'Buscar Hotéis')]"

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

        # close_stay_usa_xpath = f"//*[contains(text(), 'Continuar no Decolar Brasil')]"
        # try:
        #     self.random_wait()
        #     close_modal = self.wait.until(EC.presence_of_element_located((By.XPATH, close_stay_usa_xpath)))
        #     self.random_wait()
        #     # close_modal.click()
        #     self.move_and_click(close_modal)
        #     self.random_wait()
        # except:
        #     print(f'Element not found or webpage not loaded in time: {close_stay_usa_xpath}')

        # close_modal_xpath = f"//*[contains(@class, 'login-aggressive--button login-aggressive--button-close shifu-3-btn-ghost')]"
        # try:
        #     self.random_wait()
        #     close_modal = self.wait.until(EC.presence_of_element_located((By.XPATH, close_modal_xpath)))
        #     self.random_wait()
        #     # close_modal.click()
        #     self.move_and_click(close_modal)
        #     self.random_wait()
        # except:
        #     print(f'Element not found or webpage not loaded in time: {close_modal_xpath}')

        select_currency_xpath = f"//select[.//option[@value='USD']]"
        try:
            self.random_wait()
            select_currency = Select(self.wait.until(EC.presence_of_element_located((By.XPATH, select_currency_xpath))))
            select_currency.select_by_value('USD')
            self.random_wait()

            # Handle the alert
            alert = self.wait.until(EC.alert_is_present())
            alert.accept()
            self.random_wait()
        except:
            print(f'Element not found or webpage not loaded in time: {select_currency_xpath}')
            self.save_screenshot()
        #     raise Exception(f'Element not found or webpage not loaded in time: {select_currency_xpath}')

        # try:
        #     # Wait for the div with the `infinitescroll` attribute to not have the `-eva-3-hide` class
        #     self.wait.until(
        #         EC.presence_of_element_located(
        #             (By.XPATH, "//div[@infinitescroll and  not(contains(@class, '-eva-3-hide'))]"))
        #     )
        # except Exception:
        #     print('Timed out waiting for the div with "infinitescroll" attribute to become visible.')
        #     self.save_screenshot()

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

        # if not found:
        #     print(f"not found first try {location}")
        #     self.save_screenshot()
        #
        #     # input_filter_by_hotel_xpath = f"(//*[contains(@id, 'listMore')])[last()]/li/span/div/div/input"
        #     input_filter_by_hotel_xpath = f"//*[contains(@class, 'aut-filter-text')]/div/ul/li/span/div/div/input"
        #
        #     try:
        #         self.random_wait()
        #         self.random_wait()
        #         self.random_wait()
        #         self.random_wait()
        #         # Wait up to 10 seconds before throwing a TimeoutException unless it finds the element to return within 10 seconds
        #         input_filter_by_hotel = self.wait.until(
        #             EC.presence_of_element_located((By.XPATH, input_filter_by_hotel_xpath))
        #         )
        #         input_filter_by_hotel.location_once_scrolled_into_view
        #         self.random_wait()
        #         self.actions.move_to_element(input_filter_by_hotel).click().send_keys(location).perform()
        #     except:
        #         print(f'Element not found or webpage not loaded in time: {input_filter_by_hotel_xpath}')
        #         self.save_screenshot()
        #         raise Exception(f'Element not found or webpage not loaded in time: {input_filter_by_hotel_xpath}')
        #
        #     self.random_wait()
        #     self.random_wait()
        #     self.random_wait()
        #     self.random_wait()
        #
        #     found = look_for_hotel()
        #
        #     if not found:
        #         print(f"not found second try {location}")
        #         self.save_screenshot()
        #         raise Exception(f"Data not found")

        section_room_xpath = f"//*[contains(@data-testid, 'fn-room-item-container')]"
        # section_room_xpath = f"//*[contains(@data-testid, 'fn-desktop-availability-page-room')]"
        # section_room_xpath = f"//*[contains(@data-testid, 'fn-availability-item')]"
        # section_room_xpath = f"//*[contains(@class, 'Viewstyles__RoomStyles-sc-61otgo-4 jtsKit')]"
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
            if '/bookcore/ajax/desktop/availability/rooms' in request.path and request.response.body:
                filtered_requests.append(request)

        logger.debug(f"requests found: {filtered_requests.__len__()} out of {self.driver.requests.__len__()}")

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
        return get_standard_data_palladium(data, self.params)
