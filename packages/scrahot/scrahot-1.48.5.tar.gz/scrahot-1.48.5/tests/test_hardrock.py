import json
from pathlib import Path

import pytest
import requests
from loguru import logger

from scrahot.standard_json import get_standard_data_hardrock

base_url = 'http://localhost:5001'


@pytest.mark.order(1)
def test_hardrock():

    url = f'{base_url}/hotel-json-data/hardrock.com/Riviera Maya/2025-01-26/2025-02-01/2/0'
    response = requests.get(url)
    assert response.status_code == 200
    data = response.json()
    assert data.get('success', False), f'Not success: {response.json().get("error", None)}'
    assert data.get('currency_prices', None) == 'USD', 'Currency not expected'
    assert data.get('hotel', None) is not None, 'Hotel not found'
    assert data.get('rooms', None) is not None and len(data['rooms']) > 0, 'Rooms not found'
    room = data['rooms'][0]
    assert (room.get('beds', None) and room.get('name') and room.get('price')), 'Room data not found'

@pytest.mark.order(2)
def test_parse_hardrock():

    data_path = Path(__file__).parent / 'data' / 'hardrock.json'

    with open(data_path, 'r') as file:
        json_data = json.load(file)

    params = {'location': 'Hotel Cancun',
              'region': 'CANCUN',
              'start_date': '2025-01-05',
              'end_date': '2025-01-12',
              'adults': 2,
              'children': 0,
              }

    data = get_standard_data_hardrock(json_data, params)

    assert data.get('currency_prices', None) == 'USD', 'Currency not expected'
    assert data.get('hotel', None) is not None, 'Hotel not found'
    assert data.get('rooms', None) is not None and len(data['rooms']) > 0, 'Rooms not found'
    room = data['rooms'][0]
    assert (room.get('beds', None) and room.get('name') and room.get('price')), 'Room data not found'

    logger.info(f'Result: {data}')

