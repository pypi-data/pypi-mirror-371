import datetime
import re
import urllib.parse


from loguru import logger

from scrahot.spiders.base import BaseSelenium
from scrahot.standard_json import get_standard_data_hyatt

# import pyautogui


class HyattSelenium(BaseSelenium):

    def __init__(self):
        super().__init__('sb')

        self.name = 'hyatt'

        # Only request URLs containing "despegar" or "whatever" will now be captured
        # self.driver.scopes = [
        #     '.*hyatt.*',
        # ]

        self.params = {}

    def get_rooms(self, params):
        logger.debug(f'get_rooms: {params}')
        self.params = params

        website, region, location, start_day, start_month, start_year, end_day, end_month, end_year, adults, children, start_date, end_date = self.validate_input_data(params_required=['website', 'location', 'date_range', 'persons'])

        from seleniumbase import SB

        response = {
            "success": True,

            "search_criteria": params,

            "hotel": params.get('location'),
            "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),

            'rooms': [],
        }

        # https://seleniumbase.io/examples/cdp_mode/ReadMe/#cdp-mode-api-methods
        with SB(uc=True, test=True, locale_code="en", ad_block=True) as sb:
            # sb.activate_cdp_mode("about:blank")
            url = (f'https://www.hyatt.com/search/hotels/en-US/'
                   f'{urllib.parse.quote(location)}'
                   f'?checkinDate={start_date.strftime("%Y-%m-%d")}'
                   f'&checkoutDate={end_date.strftime("%Y-%m-%d")}'
                   f'&rooms=1&adults={adults}&kids={children}&rate=Standard'
                   )
            # url = 'https://google.com'

            # url = ("https://www.hyatt.com/search/hotels/en-US/"
            #        f"{urllib.parse.quote('Anaheim, CA, USA')}"
            #        "?checkinDate=2025-02-23"
            #        "&checkoutDate=2025-02-24"
            #        "&rooms=1&adults=1&kids=0&rate=Standard")
            logger.info(f'Opening URL: {url}')
            # return { 'success': True }
            # sb.cdp.open(url)
            sb.activate_cdp_mode(url)
            sb.sleep(2.5)

            self.save_screenshot('hyatt_home', driver=sb)

            # card_info = 'div[data-booking-status="BOOKABLE"] [class*="HotelCard"]'
            card_info = '//div[contains(@data-booking-status,"BOOKABLE")]'
            hotels = sb.cdp.select_all(card_info, timeout=60)
            logger.debug("Hyatt Hotels in %s:" % location)
            logger.debug("(" + sb.cdp.get_text("ul.b-color_text-white") + ")")
            if len(hotels) == 0:
                logger.debug("No availability over the selected dates!")

            for hotel in hotels:
                info = hotel.text.strip()
                if "Avg/Night" in info and not info.startswith("Rates from"):
                    name = info.split("  (")[0].split(" + ")[0].split(" Award Cat")[0]
                    name = name.split(" Rates from :")[0]
                    price = "?"
                    if "Rates from : " in info:
                        price = info.split("Rates from : ")[1].split(" Avg/Night")[0]
                    logger.debug("* %s => %s" % (name, price))

                # sb.cdp.click('span:contains("View Rates")')
                # sb.sleep(3)

                view_rates_parent = sb.cdp.find_element('//a[contains(., "View Rates")]')

                # Extract the href from the parent element
                view_rates_url = view_rates_parent.get_attribute("href")

                # Perform your listenXHR operations
                # sb.activate_cdp_mode("about:blank")
                # tab = sb.cdp.page
                # listenXHR(tab)
                # sb.sleep(2)

                # Navigate to the stored URL
                sb.cdp.open(view_rates_url)
                break

            sb.sleep(2)
            for i in range(15):
                sb.cdp.scroll_down(15)
            sb.sleep(5)

            tab_suites = "button[id*='tab-Suites']"
            tab_rooms = "button[id*='tab-Rooms']"

            rooms_info = "div[data-module='room-card']"
            rooms = sb.cdp.select_all(rooms_info)
            for i, room in enumerate(rooms):
                room.flash(color="44CC88")
                # view_details = "button[class*='room-details-clickable-area'][class*='b-color_text-account']"
                # details = sb.cdp.find_element(view_details)
                # details.click()

                # close_details = "i[class*='room_details_modal--close_icon']"
                # sb.cdp.find_element(close_details).click()

                room_title = "*[data-locator*='room-title']"
                title = sb.cdp.find_elements(room_title)[i]
                print(title.text)

                room_description = "*[class*='room_description']"
                description = sb.cdp.find_elements(room_description)[i]
                bed_types = re.findall(r'(\w+\s*bed)', description.text, re.I)
                if bed_types:
                    print(list(set(bed_types)))

                rate_content = "*[id*='price-length']"
                rate = sb.cdp.find_elements(rate_content)[i]
                print(rate.text)

                response['rooms'].append(
                    {
                        'name': title.text,
                        'beds': list(set(bed_types)),
                        'price': rate.text
                    }
                )

        return response

    def standardize_data(self, data):
        return get_standard_data_hyatt(data, self.params)
