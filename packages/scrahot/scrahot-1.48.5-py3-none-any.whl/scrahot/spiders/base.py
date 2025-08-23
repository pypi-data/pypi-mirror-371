import calendar
import datetime
import gzip
import logging
import random
import re
import shutil
import stat
import tempfile
import threading
import time
import platform
import zlib
from abc import abstractmethod, ABC
from pathlib import Path

import brotli
import mycdp
import seleniumbase
import zstandard
from loguru import logger
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
import seleniumwire.undetected_chromedriver.v2 as uc
import subprocess

# from fake_useragent import UserAgent
# ua = UserAgent()

from seleniumwire.thirdparty.mitmproxy.net.http import encoding

import scrahot

import os
import subprocess
import sys


def locate_and_install_certificate():
    logger.debug("Locating and installing the Selenium Wire root certificate...")
    # Step 1: Locate the selenium-wire root certificate
    try:
        # Get the installation directory of selenium-wire
        selenium_wire_location = subprocess.check_output(
            [sys.executable, '-m', 'pip', 'show', 'selenium-wire']
        ).decode('utf-8').splitlines()

        # Find the location from the pip show output
        location = None
        for line in selenium_wire_location:
            if line.startswith('Location:'):
                location = line.split(': ')[1]
                break

        if location is None:
            logger.debug("Selenium Wire is not installed.")
            return

        logger.debug(f"Looking for .pem and .crt files in: {location}")
        cert_paths = []
        for root, dirs, files in os.walk(os.path.join(location, 'seleniumwire')):
            for file in files:
                if file.endswith(('.pem', '.crt')):
                    logger.debug(f"Found certificate file: {os.path.join(root, file)}")
                    cert_paths.append(os.path.join(root, file))
        if cert_paths:
            logger.debug(f"Found {len(cert_paths)} certificate file(s).")
        else:
            logger.debug("No certificate files found.")

        for cert_path in cert_paths:
            file_name = os.path.basename(cert_path)
            target_cert_path = f'/usr/local/share/ca-certificates/{file_name}'
            logger.debug(f"Copying certificate file to: {target_cert_path}")
            subprocess.run(['sudo', 'cp', cert_path, target_cert_path])

        # Update certificates
        if cert_paths:
            result = subprocess.run(['sudo', 'update-ca-certificates'], capture_output=True, text=True)
            logger.debug(f"update-ca-certificates output: {result.stdout}")

            logger.debug(f"Selenium Wire root certificate(s) have been installed successfully on the system.")
        else:
            logger.debug("No Selenium Wire root certificate to install.")
            raise RuntimeError("Failed to locate the Selenium Wire root certificate.")

        return cert_paths[0]

    except Exception as e:
        logger.debug(f"An error occurred: {e}")
        raise RuntimeError("Failed to locate and install the Selenium Wire root certificate.")


def set_executable_permissions(file_path):
    # Set the executable permissions for the file
    st = os.stat(file_path)
    os.chmod(file_path, st.st_mode | stat.S_IEXEC)


def create_temporary_file(source_file_path):
    # Create a temporary file
    _, ext = os.path.splitext(source_file_path)
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
        # Copy content from the source file to the temporary file
        shutil.copyfile(source_file_path, temp_file.name)
        temp_file_path = temp_file.name

    # Set the executable permissions for the temporary file
    set_executable_permissions(temp_file_path)

    return temp_file_path


DEFAULT_WAIT_TIMEOUT = 30


class BaseSelenium(ABC):
    def __init__(self, driver_type='uc'):
        self.user_agent = None
        self.params = None
        self.name = 'base'
        self.records_path = Path(scrahot.__file__).parent / 'records'
        self.record_execution = False

        self.xhr_requests = []
        self.last_xhr_request = None

        # Determine the platform (Windows or Linux)
        self.is_windows = platform.system() == 'Windows'

        # Set up environment variables
        self.display = os.getenv('DISPLAY', ":99")
        self.resolution = "1920x1080"  # os.getenv('RESOLUTION', '1920x1080x24')
        self.recording_dir = os.path.join(scrahot.__path__[0], 'records')  # os.environ['RECORDING_DIR']
        self.recording_process = None
        self.output_filename = ""

        self.chrome_version = "121"
        self.chromedriver_version = "121"

        self.get_versions()

        # sw_cert_path = locate_and_install_certificate()

        # Usage
        # if os.getenv('ENV') == 'prod':
        if not self.is_windows:
            self.chromedriver_path = os.getenv('CHROMEDRIVER_PATH', '/usr/local/bin/chromedriver')
        else:
            self.chromedriver_path = rf"{os.path.join(scrahot.__path__[0], 'chromedriver.exe')}"

        logger.debug(f"chromedriver path: {self.chromedriver_path}")

        # Get a random browser user-agent string
        # random_user_agent = ua.chrome
        # logger.debug(f'fake UA: {random_user_agent}')

        original_block = ("{window.cdc_adoQpoasnfa76pfcZLmcfl_Array = window.Array;"
                          "window.cdc_adoQpoasnfa76pfcZLmcfl_Object = window.Object;"
                          "window.cdc_adoQpoasnfa76pfcZLmcfl_Promise = window.Promise;"
                          "window.cdc_adoQpoasnfa76pfcZLmcfl_Proxy = window.Proxy;"
                          "window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol = window.Symbol;"
                          "window.cdc_adoQpoasnfa76pfcZLmcfl_JSON = window.JSON;}")

        # Create a benign block of the same length as the original block
        benign_block = '{}'
        benign_block = benign_block.ljust(len(original_block))

        if self.patch_chromedriver(self.chromedriver_path, original_block, benign_block):
            logger.debug(f"Chromedriver patched successfully at {self.chromedriver_path}")
        else:
            logger.debug("Failed to patch the chromedriver.")

        # Set the logging level for seleniumwire to ERROR
        logging.getLogger('seleniumwire').setLevel(logging.ERROR)
        logging.getLogger('selenium').setLevel(logging.ERROR)
        logging.getLogger('scrapy').setLevel(logging.ERROR)
        logging.getLogger('urllib3').setLevel(logging.ERROR)
        logging.getLogger('websockets.client').setLevel(logging.ERROR)
        logging.getLogger('seleniumbase').setLevel(logging.ERROR)

        # Installs chromedriver which corresponds to the main Chrome automatically
        # chromedriver_autoinstaller.install()

        # options = webdriver.ChromeOptions()
        options = uc.ChromeOptions()

        # https://stackoverflow.com/a/77299487/1451885
        # if the seleniumwire certificate is not installed on authorities in chrome enable this flags.
        options.accept_insecure_certs = True
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-certificate-errors-spki-list')
        options.add_argument('--allow-running-insecure-content')

        # options.add_argument("--disable-notifications")
        # options.add_argument("--disable-popup-blocking")

        # prefs = {
        #     "profile.default_content_setting_values.notifications": 2
        # }
        # options.add_experimental_option("prefs", prefs)

        # options.add_argument("enable-features=NetworkServiceInProcess")e
        # options.add_argument("disable-features=NetworkService")

        # options.set_capability(DesiredCapabilities.CHROME, "localhost:4444")
        # options = webdriver.FirefoxOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--start-maximized")
        if os.getenv('HEADLESS', 'false') == 'true':
            options.add_argument("--headless")

        options.add_argument('--verbose')
        options.add_argument(f"--log-path={os.path.join(self.recording_dir, 'chromedriver.log')}")

        # prefs = {}
        # prefs["profile.managed_default_content_settings.images"] = 2
        # options.add_experimental_option("prefs", prefs)
        # options.add_argument("--blink-settings=imagesEnabled=false")
        options.add_argument("--remote-debugging-host=127.0.0.1")
        options.add_argument('--remote-debugging-port=9222')
        # Disable selenium wire headers
        # options.add_argument("disable-extensions")
        # options.add_argument("disable-popup-blocking")
        # options.add_argument('--auto-open-devtools-for-tabs')   # automatically open dev tools on every new tab
        # proxy_ip = os.getenv('PROXY_IP', '34.120.231.30')
        # proxy_port = os.getenv('PROXY_PORT', '80')
        # options.add_argument(f"--proxy-server={proxy_ip}:{proxy_port}")
        options.add_argument(
            f"--proxy-server=http://127.0.0.1:{os.getenv('MITMPROXY_PORT', 8787)}")  # Default mitmproxy port

        # profile_path = f"C:\\tmp\\UserData"
        # options.add_argument(f'--user-data-dir={profile_path}')

        bdr_extension_path = os.path.join(scrahot.__path__[0], 'block_domain_extension').replace("\\", "\\\\")
        logger.debug(f"Using BDR extension: {bdr_extension_path}")
        options.add_argument(f"--load-extension={bdr_extension_path}")
        options.add_extension(f"{bdr_extension_path}.crx")

        # Adding argument to disable the AutomationControlled flag
        options.add_argument("--disable-blink-features=AutomationControlled")

        # # Exclude the collection of enable-automation switches
        # options.add_experimental_option("excludeSwitches", ["enable-automation"])
        #
        # # Turn-off userAutomationExtension
        # options.add_experimental_option("useAutomationExtension", False)

        def custom_decoder(encoded_bytes, encoding):
            if encoding == 'application/json; charset=utf-8':
                return encoded_bytes.decode('utf-8')
            raise LookupError(f'Unknown encoding: {encoding}')

        # Define Selenium Wire options
        options_selenium_wire = {
            # 'custom_response_handler': custom_decoder,
            # 'decode_compressed_response': False,
            # 'proxy': {
            #     'http': 'http://user:pass@ip:port',
            #     'https': 'https://user:pass@ip:port',
            #     'no_proxy': 'localhost,127.0.0.1'
            # },
            # 'custom_headers': {
            #     f'Sec-Ch-Ua': f'"Google Chrome";v="{self.chrome_version.split(".")[0]}", "Chromium";v="{self.chrome_version.split(".")[0]}", "Not?A_Brand";v="24"',
            #     f'Sec-Ch-Ua-Mobile': '?0',
            #     f'Sec-Ch-Ua-Platform': '"Linux"',
            #     f'Sec-Fetch-Dest': 'script',
            #     f'Sec-Fetch-Mode': 'no-cors',
            #     f'Sec-Fetch-Site': 'same-origin',
            #     # f'User-Agent': f'Mofzilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            # },
            'enable_console_log': True,
            'log_level': 'ERROR',  # Use 'ERROR' to log only errors, 'WARNING' for warnings and errors
            # 'auto_config': False,
            # 'ca_cert': sw_cert_path, # rf"{os.path.join(scrahot.__path__[0], 'ca.crt')}",
            # 'addr': '0.0.0.0',
            # 'port': 5002,
            # 'proxy': {
            #     'http': 'http://scrahot:5002',
            #     'https': 'http://scrahot:5002',
            #     'no_proxy': 'localhost,127.0.0.1',
            # }
        }

        # Initializing a list with two Useragents
        useragentarray = [
            f"Mozilla/5.0 ({self.is_windows and 'Windows NT 10.0; Win64; x64' or 'X11; Linux x86_64'}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{self.chrome_version.split('.')[0]}.0.0.0 Safari/537.36",
            f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        ]

        # selenium webremote
        # you are going to tell selenium the IP where the code will run
        # replace scrap with the IP, I use scrap because my docker-compose file uses that name
        # options.add_argument('--proxy-server=scrahot:5002')
        # self.driver = webdriver.Remote(command_executor='http://selenium-hub:4444',
        #                                options=options,
        #                                seleniumwire_options=options_selenium_wire)
        # # self.driver.execute("Network.setUserAgentOverride", {"userAgent": useragentarray[0]})

        # selenium local
        if os.getenv('ENV') == 'prod':
            service = Service(executable_path=rf"{self.chromedriver_path}")
        else:
            service = Service(executable_path=self.chromedriver_path)

        logger.debug(f"Headless {os.getenv('HEADLESS', 'false') == 'true'}")
        service.port = 5003
        self.driver = None
        self.driver_sb = None
        try:
            chrome_driver_tmp = create_temporary_file(self.chromedriver_path)
            if driver_type == 'sb':
                # self.driver_sb: seleniumbase.Driver = seleniumbase.Driver(uc=True, locale_code="en", ad_block=True,
                #                                                           headless=True)

                return
            else:
                self.driver = uc.Chrome(service=service,
                                        version_main=int(self.chrome_version.split(".")[0]),
                                        options=options,
                                        headless=os.getenv('HEADLESS', 'false') == 'true',
                                        use_subprocess=False,
                                        driver_executable_path=chrome_driver_tmp,
                                        seleniumwire_options=options_selenium_wire)

        except Exception as e:
            logger.debug(f"error initializing driver: {e}")
            raise RuntimeError("Failed to initialize the driver")
        self.user_agent = useragentarray[0]
        self.set_user_agent(self.user_agent)
        # Setting user agent iteratively as Chrome 108 and 107
        # self.driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": self.user_agent})
        # self.driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": random_user_agent})

        # Changing the property of the navigator value for webdriver to undefined
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        # Wait for the element to be visible and enabled
        self.wait = WebDriverWait(self.driver, DEFAULT_WAIT_TIMEOUT)
        self.actions = ActionChains(self.driver)

        def my_request_interceptor(request):
            # print('Request URL:', request.url)
            if 'datadome' in request.url or 'datadome' in request.host or 'datadome' in request.path:
                # print('Blocked request to datadome', request.url)
                request.abort()
            else:
                del request.headers['Selenium']  # Remove Selenium header if it exists
                del request.headers['selenium']  # Just in case if header name is in lowercase
                del request.headers['Sec-Ch-Device-Memory']  # Just in case if header name is in lowercase
                del request.headers['Sec-Ch-Ua-Arch']  # Just in case if header name is in lowercase
                del request.headers['Sec-Ch-Ua-Model']  # Just in case if header name is in lowercase
                del request.headers['Sec-Ch-Ua-Full-Version-List']  # Just in case if header name is in lowercase

                ## Do something with the request
                custom_headers = {
                    f'Sec-Ch-Ua': f'"Google Chrome";v="{self.chrome_version.split(".")[0]}", "Chromium";v="{self.chrome_version.split(".")[0]}", "Not?A_Brand";v="24"',
                    # f'Sec-Ch-Ua-Arch': 'x86',
                    f'Sec-Ch-Ua-Mobile': '?0',
                    f'Sec-Ch-Ua-Platform': f'"{self.is_windows and "Windows" or "Linux"}"',
                    f'Sec-Fetch-Dest': 'document',
                    f'Sec-Fetch-Mode': 'navigate',
                    f'Sec-Fetch-Site': 'none',
                    f'Sec-Fetch-User': '?1',
                    f'Upgrade-Insecure-Requests': '1',
                    f'Accept-Language': 'en-US,en;q=0.9',
                    f'User-Agent': useragentarray[0],
                    # f'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                }

                for i, v in custom_headers.items():
                    del request.headers[i]  # Delete the header first
                    request.headers[i] = v

        def my_response_interceptor(request, response):
            # A response interceptor takes two args (request, response)
            # # Do something

            # # print('Request URL:', request.url)
            # print('ASDFASFSADF:', 'api-js.datadome.co' in request.url)
            #
            # # Block PNG, JPEG and GIF images
            # if 'api-js.datadome.co' in request.url:
            #
            #     print('Blocked request to datadome', request.url)
            #
            #     # Clear all cookies
            #     self.driver.delete_all_cookies()
            #     print('Blocked request to datadome2', request.url)
            #     request.abort()

            pass

        self.driver.request_interceptor = my_request_interceptor

        self.driver.response_interceptor = my_response_interceptor

        # setting the timeout for page load to 60 seconds
        self.driver.set_page_load_timeout(600)

        # Execute CDP command to remove navigator.webdriver property
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                   Object.defineProperty(navigator, 'webdriver', {
                     get: () => undefined
                   })
               """
        })

    def __enter__(self):
        logger.debug("Entering the block")
        # initialize resources
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.debug("Exiting the block")
        if exc_type is not None:
            logger.debug(f"Exeption ocurred, saving screenshot.")
            # print(f"An exception of type {exc_type} occurred with value {exc_val}.")
            # print(f"Traceback: {exc_tb}")
            self.save_screenshot()

        if os.getenv('ENV') == 'prod' and self.driver:
            self.driver.quit()
        # clean up resources here

    @abstractmethod
    def get_rooms(self, params):
        pass

    def set_user_agent(self, user_agent=None):
        if user_agent is None:
            user_agent = self.user_agent
        self.driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": user_agent})

    def exit_driver(self):
        logger.debug('Closing driver')
        self.driver.quit()

    def random_wait(self):
        time_to_wait = random.randint(1, 2)  # Replace 'a' and 'b' with the range of seconds you want
        # print(f'random_wait: {time_to_wait}')
        time.sleep(time_to_wait)
        # print('random_wait: done')

    def save_screenshot(self, msg=None, driver=None):
        now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d-%H-%M-%S-%f')
        msg = "_" + msg if msg else ""
        path = self.records_path / f'{self.name}'
        os.makedirs(path, exist_ok=True)
        if driver:
            driver.save_screenshot(str((path / f's_{self.name}_{now}{msg}.png').absolute().resolve()))
        elif self.driver:
            self.driver.save_screenshot((path / f's_{self.name}_{now}{msg}.png').absolute().resolve())
        elif self.driver_sb:
            self.driver_sb.save_screenshot((path / f's_{self.name}_{now}{msg}.png').absolute().resolve())
        else:
            logger.warning(f"No driver found to save screenshot.")

    def save_element_screenshot(self, element, msg=None):
        now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d-%H-%M-%S-%f')
        msg = "_" + msg if msg else ""
        path = self.records_path / f'{self.name}'
        os.makedirs(path, exist_ok=True)
        filename = str((path / f's_{self.name}_{now}{msg}.png').absolute().resolve())
        element.screenshot(filename)

    # Function to extract numeric version
    def extract_numeric_version(self, version_string):
        match = re.search(r'(\d+\.\d+\.\d+\.\d+)', version_string)
        return match.group(0) if match else None

    def get_versions(self):

        # Set CHROMEDRIVER_PATH environment variable if not defined
        if 'CHROMEDRIVER_PATH' not in os.environ:
            if self.is_windows:
                default_chromedriver_path = os.path.join(scrahot.__path__[0],
                                                         'chromedriver.exe')  # Update this path as needed
            else:
                default_chromedriver_path = os.path.join(scrahot.__path__[0],
                                                         'chromedriver')  # '/usr/local/bin/chromedriver'
            os.environ['CHROMEDRIVER_PATH'] = default_chromedriver_path

        # Set the commands based on the platform
        chrome_command = "chrome.exe --version" if self.is_windows else "google-chrome --version"
        # Now you can access CHROMEDRIVER_PATH and it will be set to your default if it wasn't already defined
        chromedriver_path = os.getenv('CHROMEDRIVER_PATH', '/usr/local/bin/chromedriver')
        logger.debug(f'ChromeDriver path is set to: {chromedriver_path}')

        # # Windows needs the full path to the executable for subprocess to work without permission issues
        # if is_windows and not os.path.isabs(chromedriver_path):
        #     chromedriver_path = os.path.join(os.getcwd(), chromedriver_path)
        chromedriver_command = chromedriver_path + " --version"

        try:
            # Get Chrome version
            chrome_version_result = subprocess.run(chrome_command, capture_output=True, text=True, shell=True,
                                                   check=True, timeout=10)
            self.chrome_version = self.extract_numeric_version(chrome_version_result.stdout.strip())
            logger.debug(f"Chrome version: {self.chrome_version}")

            # Get ChromeDriver version
            chromedriver_version_result = subprocess.run(chromedriver_command, capture_output=True, text=True,
                                                         shell=True, check=True, timeout=10)
            self.chromedriver_version = self.extract_numeric_version(chromedriver_version_result.stdout.strip())
            logger.debug(f"ChromeDriver version: {self.chromedriver_version}")


        except subprocess.TimeoutExpired:
            logger.debug("The command timed out")
        except subprocess.CalledProcessError as e:
            logger.debug(f"The command '{e.cmd}' failed with return code {e.returncode}")
        except Exception as e:
            logger.debug(f"An error occurred: {e}")

    def replace_string_in_file(self, file_path, search_string, replace_string):
        # Make sure the replacement string is the same length as the search string
        if len(search_string) != len(replace_string):
            logger.debug("The search string and replace string must be the same length.")
            return False

        # Read the file content
        with open(file_path, 'rb') as file:
            file_content = file.read()

        # Replace the string
        new_content = file_content.replace(search_string.encode(), replace_string.encode())

        # Write the new content to the file
        with open(file_path, 'wb') as file:
            file.write(new_content)

        return True

    def patch_chromedriver(self, file_path, original_block, replacement):
        # Ensure the replacement block is the same length as the original block
        if len(original_block) != len(replacement):
            replacement = replacement.ljust(len(original_block))

            # Check if the file has already been patched
        if self.has_been_patched(file_path, replacement):
            logger.debug("Chromedriver has already been patched.")
            return True

        # Read the file content
        with open(file_path, 'rb') as file:
            file_content = file.read()

        # Replace the block
        new_content = file_content.replace(original_block.encode(), replacement.encode())

        # Write the new content to the file
        with open(file_path, 'wb') as file:
            file.write(new_content)

        return True

    def has_been_patched(self, file_path, benign_block):
        # Read the file content
        with open(file_path, 'rb') as file:
            file_content = file.read()

        # Check if the benign block is already in the file content
        return benign_block.encode() in file_content

    # Function to start recording
    def start_recording(self):
        now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d-%H-%M-%S-%f')
        path = self.records_path / f'{self.name}'
        os.makedirs(path, exist_ok=True)
        self.output_filename = path / f"v_{self.name}_{now}.mp4"
        command = [
            'ffmpeg',
            '-video_size', str(self.resolution),
            '-framerate', '15',
            '-f', 'x11grab',
            '-i', f'{self.display}.0',
            '-c:v', 'libx264',
            '-preset', 'veryfast',
            '-pix_fmt', 'yuv420p',
            str(self.output_filename)
        ]

        self.recording_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.recording_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                                  bufsize=10 ** 8)

        def read_output(pipe, func):
            while True:
                line = pipe.readline()
                if line:
                    func(line.decode())
                else:
                    break

        threading.Thread(target=read_output, args=(self.recording_process.stdout, print)).start()
        threading.Thread(target=read_output, args=(self.recording_process.stderr, print)).start()

        # stdout, stderr = self.recording_process.communicate()
        # if stderr:
        #     print(f"Error: {stderr.decode()}")
        # else:
        #     print(f"Recording started, saving to {self.output_filename}")

    def stop_recording(self):
        self.recording_process.terminate()
        self.recording_process.wait()
        logger.debug("Recording stopped")

    def run(self, *args, **kwargs):
        if not self.is_windows:
            if self.record_execution:
                # Start recording
                self.start_recording()
            pass
        result = None
        try:
            # Pass all arguments to the scrape method
            result = self.get_rooms(*args, **kwargs)
            logger.info(f"Run successful, result: {result}")
        finally:
            if not self.is_windows:
                if self.record_execution:
                    # Stop recording
                    self.stop_recording()
                pass

        return result

    def get_rooms(self, params):
        # This method should be implemented by subclasses
        raise NotImplementedError("Subclasses must implement this method")

    def validate_input_data(self, params=None, params_required=None):
        if params is None and not self.params is None:
            params = self.params
        else:
            raise ValueError("No parameters provided.")
        if params_required is None:
            params_required = ['website', 'location', 'date_range', 'persons']

        today = datetime.datetime.now()

        # Validate website and location
        website = params.get('website')
        if not website or not isinstance(website, str):
            raise ValueError("Invalid website.")

        region = params.get('region', None)
        if 'region' in params_required:
            if not region or not isinstance(region, str):
                raise ValueError("Invalid region type.")
            if 'undefined' in region:
                raise ValueError(f'Invalid region: "{region}"')

        location = params.get('location')
        if not location or not isinstance(location, str) and 'undefined' in location:
            raise ValueError("Invalid location.")

        if 'undefined' in location:
            raise ValueError(f'Invalid location: "{location}"')

        # Validate date range
        start_date = datetime.datetime.strptime(params.get('date_range').get('start'), '%Y-%m-%d')
        end_date = datetime.datetime.strptime(params.get('date_range').get('end'), '%Y-%m-%d')

        if start_date < today:
            raise ValueError("Start date cannot be in the past.")
        if end_date < start_date:
            raise ValueError("End date must be after start date.")

        start_day = start_date.day
        start_month = calendar.month_name[start_date.month]
        start_year = start_date.year

        end_day = end_date.day
        end_month = calendar.month_name[end_date.month]
        end_year = end_date.year

        # Validate persons
        adults = params.get('persons').get('adults')
        children = params.get('persons').get('children')

        try:
            adults = int(adults)
            children = int(children)
            if adults < 0 or children < 0:
                raise ValueError("Number of adults and children cannot be negative.")
        except (ValueError, TypeError):
            raise ValueError("Invalid number of adults or children.")

        return website, region, location, start_day, start_month, start_year, end_day, end_month, end_year, adults, children, start_date, end_date

    def wait_for_all_elements(self, xpath, raise_exception=True, retries=3, timeout=None):
        if timeout:
            self.wait = WebDriverWait(self.driver, timeout)
        attempt = 0
        while attempt < retries:
            try:
                elements = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
                self.wait = WebDriverWait(self.driver, DEFAULT_WAIT_TIMEOUT)
                return elements
            except Exception as e:
                logger.debug(f'Attempt {attempt + 1} failed: {e}')
                attempt += 1
                time.sleep(1)
        logger.debug(f'Element not found or webpage not loaded in time: {xpath}')
        if raise_exception:
            self.save_screenshot()
            raise Exception(f'Element not found or webpage not loaded in time: {xpath}')

    def wait_for_element(self, xpath, raise_exception=True, retries=3, timeout=None):
        if timeout:
            self.wait = WebDriverWait(self.driver, timeout)
        attempt = 0
        while attempt < retries:
            try:
                element = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                self.wait = WebDriverWait(self.driver, DEFAULT_WAIT_TIMEOUT)
                return element
            except Exception as e:
                logger.debug(f'Attempt {attempt + 1} failed: {e}')
                attempt += 1
                time.sleep(1)

        logger.debug(f'Element not found or webpage not loaded in time: {xpath}')
        if raise_exception:
            self.save_screenshot()
            raise Exception(f'Element not found or webpage not loaded in time: {xpath}')

    def wait_and_click_element(self, xpath, raise_exception=True, retries=3, timeout=None):
        attempt = 0
        while attempt < retries:
            try:
                element = self.wait_for_element(xpath, raise_exception=raise_exception, timeout=timeout)
                # element.click()
                self.move_and_click(element)
                return element
            except Exception as e:
                logger.debug(f'Attempt {attempt + 1} failed: {e}')
                attempt += 1
                time.sleep(1)  # Optional: wait a bit before retrying
        logger.debug(f'Element not found or webpage not loaded in time: {xpath}')
        if raise_exception:
            self.save_screenshot()
            raise Exception(f'Element not found or webpage not loaded in time: {xpath}')
        return None

    def click_element(self, xpath, raise_exception=True, retries=3, timeout=None):
        attempt = 0
        while attempt < retries:
            try:
                element = self.driver.find_element(By.XPATH, xpath)
                element.click()
                return
            except Exception as e:
                logger.debug(f'Attempt {attempt + 1} failed: {e}')
                attempt += 1
                time.sleep(1)
        logger.debug(f'Element not found or webpage not loaded in time: {xpath}')
        if raise_exception:
            self.save_screenshot()
            raise Exception(f'Element not found or webpage not loaded in time: {xpath}')

    def move_and_click(self, element):
        # Move to the element and click on it
        # self.driver.execute_script("arguments[0].scrollIntoView();", element)
        # element.click()

        # First, create an instance of ActionChains
        # self.actions = ActionChains(self.driver)

        # Get the size of the button
        button_size = element.size
        button_width = int(button_size['width'] * 0.5)
        button_height = int(button_size['height'] * 0.5)

        # Calculate a random offset within the bounds of the button
        x_offset = random.randint(-button_width // 2, button_width // 2)
        y_offset = random.randint(-button_height // 2, button_height // 2)

        # Then, move to your button element with a random offset
        self.actions.move_to_element_with_offset(element, x_offset, y_offset)

        # # Perform the move action
        # actions.perform()

        # Optionally, you can add some pause
        self.actions.pause(random.uniform(0.5, 1.5))  # Pause for a random time between 0.5 and 1.5 seconds

        # Now, click on the button
        self.actions.click()

        # Perform the click action
        self.actions.perform()

    def decode_body(self, response):
        # logger.debug(f"Decoding response: {response}")
        # logger.debug(f"Decoding response body: {response.body}")
        # logger.debug(f"Decoding response body: {response.headers}")
        content_encoding = response.headers.get('Content-Encoding', '').lower()
        content_type = response.headers.get('Content-Type', '').lower()

        encodings = [enc.strip() for enc in content_encoding.split(',')]

        response_body = response.body
        for encoding in encodings:
            if 'gzip' == encoding:
                try:
                    response_body = gzip.decompress(response_body)
                except UnicodeDecodeError as e:
                    raise UnicodeDecodeError(f"Failed to decode gzip-compressed response: {e}")
            elif 'deflate' == encoding:
                try:
                    response_body = encoding.decode(response_body, 'deflate')
                except UnicodeDecodeError as e:
                    raise UnicodeDecodeError(f"Failed to decode deflate-compressed response: {e}")
            elif 'br' == encoding:
                try:
                    response_body = brotli.decompress(response_body)
                except UnicodeDecodeError as e:
                    raise UnicodeDecodeError(f"Failed to decode br-compressed response: {e}")
            elif 'compress' == encoding:
                try:
                    response_body = zlib.decompress(response_body, zlib.MAX_WBITS | 16)
                except UnicodeDecodeError as e:
                    raise UnicodeDecodeError(f"Failed to decode compress-compressed response: {e}")
            elif 'zstd' == encoding:
                try:
                    response_body = zstandard.decompress(response_body)
                except UnicodeDecodeError as e:
                    raise UnicodeDecodeError(f"Failed to decode zstd-compressed response: {e}")

        if 'application/json' in content_type:
            charset = 'utf-8'  # Default charset for JSON
            if 'charset=' in content_type:
                charset = content_type.split('charset=')[-1]
            try:
                response_body = response_body.decode(charset)
            except UnicodeDecodeError:
                raise UnicodeDecodeError(f"Failed to decode JSON response: {e}")
        else:
            # Fallback to default decoding mechanism if not JSON or gzip
            try:
                response_body = response_body.decode('utf-8')
            except UnicodeDecodeError as e:
                raise UnicodeDecodeError(f"Failed to decode response: {e}")

        return response_body

    async def send_handler(self, event: mycdp.network.RequestWillBeSent):
        r = event.request
        s = f"{r.method} {r.url}"
        for k, v in r.headers.items():
            s += f"\n\t{k} : {v}"
        logger.debug("*** ==> RequestWillBeSent <== ***")
        logger.debug(s)

    async def receive_handler(self, event: mycdp.network.ResponseReceived):
        logger.debug("*** ==> ResponseReceived <== ***")
        logger.debug(event.response)

    def listenXHR(self, page):
        async def handler(evt):
            # Get AJAX requests
            if evt.type_ is mycdp.network.ResourceType.XHR:
                self.xhr_requests.append([evt.response.url, evt.request_id])
                self.last_xhr_request = time.time()

        page.add_handler(mycdp.network.ResponseReceived, handler)

    async def receiveXHR(self, page, requests=None):
        if requests is None:
            requests = self.xhr_requests
        responses = []
        retries = 0
        max_retries = 5
        # Wait at least 2 seconds after last XHR request for more
        while True:
            if self.last_xhr_request is None or retries > max_retries:
                break
            if time.time() - self.last_xhr_request <= 2:
                retries = retries + 1
                time.sleep(2)
                continue
            else:
                break
        await page
        # Loop through gathered requests and get response body
        for request in requests:
            try:
                res = await page.send(mycdp.network.get_response_body(request[1]))
                if res is None:
                    continue
                responses.append({
                    "url": request[0],
                    "body": res[0],
                    "is_base64": res[1],
                })
            except Exception as e:
                print("Error getting response:", e)
        return responses

    def _configure_sb_logging(self):
        """Configure SeleniumBase logging to work with loguru"""
        # Set SeleniumBase logging level
        sb_logger = logging.getLogger('seleniumbase')
        sb_logger.setLevel(logging.DEBUG)

        # Create a custom handler that forwards to loguru
        class LoguruHandler(logging.Handler):
            def emit(self, record):
                logger.debug(f"LoguruHandler: {record}")
                try:
                    level = record.levelname
                    message = record.getMessage()
                    if level == 'ERROR':
                        logger.error(f"SeleniumBase: {message}")
                    elif level == 'WARNING':
                        logger.warning(f"SeleniumBase: {message}")
                    elif level == 'DEBUG':
                        logger.debug(f"SeleniumBase: {message}")
                    else:
                        logger.info(f"SeleniumBase: {message}")
                except Exception:
                    pass

        # Add the handler to SeleniumBase logger
        handler = LoguruHandler()
        sb_logger.addHandler(handler)
        sb_logger.propagate = False
