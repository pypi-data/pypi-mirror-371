import argparse
import datetime
import os.path
import sys
import threading
import traceback
import uuid

from flask import Flask, jsonify
from loguru import logger
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

from scrahot.spiders.bestday import BestdaySeleniumBase
from scrahot.spiders.booking import BookingSeleniumBase
from scrahot.spiders.cvc import  CvcSeleniumBase
from scrahot.spiders.decolar import DecolarSelenium, DecolarSeleniumBase
from scrahot.spiders.despegar import DespegarSelenium
from scrahot.spiders.expedia import ExpediaSeleniumBase
from scrahot.spiders.hardrock import HardrockSelenium
from scrahot.spiders.hoteles import HotelesSeleniumBase
from scrahot.spiders.hyatt import HyattSelenium
from scrahot.spiders.palladium import PalladiumSelenium
from scrahot.spiders.test import TestSelenium
import subprocess
import atexit

app = Flask(__name__)


settings = get_project_settings()


@app.route('/hotel-json-data/<website>/<region>/<location>/<start>/<end>/<adults>/<children>', methods=['GET'])
def hotel_region_json_data(website: str, region: str, location: str, start: str, end: str, adults: int, children: int):
    identifier = uuid.uuid4()
    params = {
        'website': website,
        'region': region,
        'location': location,
        'date_range': {'start': start, 'end': end},
        'persons': {'adults': int(adults), 'children': int(children)},
        'uuid': identifier
    }

    logger.debug(f"Starting request for {website} with params: {params}")

    data = {}
    try:
        if "cvc.com" in website:
            with CvcSeleniumBase() as x:
                data = x.run(params)
            pass
        elif "palladium.com" in website:
            with PalladiumSelenium() as x:
                data = x.run(params)
            pass

        # elif "test.com" in website:
        #     with TestSelenium() as x:
        #         print("Inside the 'with' block")
        #         data = x.run(params)
        #     pass
        else:
            raise Exception(f"Website not supported: {website}")
    except Exception as e:
        logger.debug(f"General Error: {e}")
        logger.debug(traceback.format_exc())
        data = {'error': str(e), "search_criteria": params, "success": False, "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")}

    # Return a response to the client
    return data

@app.route('/hotel-json-data/<website>/<location>/<start>/<end>/<adults>/<children>', methods=['GET'])
def hotel_json_data(website: str, location: str, start: str, end: str, adults: int, children: int):
    identifier = uuid.uuid4()
    params = {
        'website': website,
        'location': location,
        'date_range': {'start': start, 'end': end},
        'persons': {'adults': int(adults), 'children': int(children)},
        'uuid': identifier
    }

    logger.debug(f"Starting request for {website} with params: {params}")

    data = {}
    try:
        if "hoteles.com" in website:
            with HotelesSeleniumBase() as x:
                data = x.run(params)
        elif "expedia.com" in website:
            with ExpediaSeleniumBase() as x:
                data = x.run(params)
            pass
        elif "despegar.com" in website:
            with DespegarSelenium() as x:
                data = x.run(params)
            pass
        elif "bestday.com.mx" in website:
            with BestdaySeleniumBase() as x:
                data = x.run(params)
            pass
        elif "booking.com" in website:
            with BookingSeleniumBase() as x:
                data = x.run(params)
            # raise Exception(f"Website in maintaining mode: {website}")
            pass
        elif "decolar.com" in website:
            with DecolarSeleniumBase() as x:
            # with DecolarSelenium() as x:
                data = x.run(params)
            pass
        elif "hardrock.com" in website:
            with HardrockSelenium() as x:
                data = x.run(params)
            pass
        elif "hyatt.com" in website:
            with HyattSelenium() as x:
                data = x.run(params)
            pass
        # elif "cvc.com" in website:
        #     with CvcSelenium() as x:
        #         data = x.run(params)
        #     pass
        # elif "test.com" in website:
        #     with TestSelenium() as x:
        #         print("Inside the 'with' block")
        #         data = x.run(params)
        #     pass
        else:
            raise Exception(f"Website not supported: {website}")
    except Exception as e:
        logger.debug(f"General Error: {e}")
        logger.debug(traceback.format_exc())
        data = {'error': str(e), "search_criteria": params, "success": False, "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")}

    # Return a response to the client
    return data

@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify(message='Hello, World!')


# Check if this is the reloaded process when running in debug mode
if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    # Define the custom port for mitmproxy
    custom_port = int(os.environ.get('MITMPROXY_PORT', 8786))  # Replace with your desired port number
    os.putenv('MITMPROXY_PORT', str(custom_port))

    path_to_script = os.path.join(os.path.abspath(__file__).replace("app.py", ""), 'scrahot',
                                  'proxy_interceptor.py')
    print(f'Path to script: {path_to_script}')
    # Start mitmproxy as a background process
    mitmproxy_process = subprocess.Popen(
        ['mitmdump', '-s', path_to_script, '-p', str(custom_port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    def print_output(process):
        # Print standard output and standard error from mitmproxy
        stdout, stderr = process.communicate()
        print('Mitmproxy Output:', stdout.decode())
        print('Mitmproxy Error:', stderr.decode(), file=sys.stderr)

    # Function to stop mitmproxy when the Flask app is about to shut down
    def stop_mitmproxy():
        if mitmproxy_process:
            mitmproxy_process.terminate()
            mitmproxy_process.wait()

    # Register the function to be called when the app process exits
    atexit.register(stop_mitmproxy)

    def print_output(process):
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip().decode())

    # Start the thread to print mitmproxy output
    thread = threading.Thread(target=print_output, args=(mitmproxy_process,))
    thread.start()

def main():
    parser = argparse.ArgumentParser(description='Run scrahot Flask app')
    parser.add_argument('--port', type=int, default=5005, help='Flask app port (default: 5005)')
    parser.add_argument('--proxy-port', type=int, help='Mitmproxy port (auto-calculated if not provided)')

    args = parser.parse_args()

    # Auto-calculate proxy port if not provided (Flask port + 1000)
    proxy_port = args.proxy_port or (args.port + 1000)

    # Set the proxy port for this instance
    os.environ['MITMPROXY_PORT'] = str(proxy_port)

    # configure logging, environment, etc.
    configure_logging()
    app.run(host="127.0.0.1", port=5005, debug=True)

    # configure_logging()
    # # app.run(debug=True)
    # app.run(host='127.0.0.1', port=5005, debug=True)
    # # use this for compiling the .exe for hyacc
    # # app.run(host='127.0.0.1', port=5005, debug=False)

if __name__ == '__main__':
    main()
