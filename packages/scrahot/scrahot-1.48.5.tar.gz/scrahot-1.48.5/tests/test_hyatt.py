import json
from pathlib import Path

import pytest
import requests
from loguru import logger

from scrahot.standard_json import get_standard_data_hyatt

base_url = 'http://localhost:5005'


@pytest.mark.order(1)
def test_hyatt():

    # url = f'{base_url}/hotel-json-data/hyatt.com/Secrets Moxché/2025-02-08/2025-02-19/2/0'
    url = f'{base_url}/hotel-json-data/hyatt.com/Secrets Moxché/2025-04-08/2025-04-15/2/0'
    response = requests.get(url)
    assert response.status_code == 200
    data = response.json()
    assert data.get('success', False), f'Not success: {response.json().get("error", None)}'
    assert data.get('currency_prices', None) == 'USD', 'Currency not expected'
    assert data.get('hotel', None) is not None, 'Hotel not found'
    assert data.get('rooms', None) is not None and len(data['rooms']) > 0, 'Rooms not found'
    room = data['rooms'][0]
    assert (room.get('beds', None) and room.get('name') and room.get('price')), 'Room data not found'

@pytest.mark.order(1)
def test_get_requests_hyatt():

    url = f'{base_url}/hotel-json-data/hyatt.com/Secrets Moxché/2025-01-13/2025-01-19/2/0'
    response = requests.get(url)
    assert response.status_code == 200
    data = response.json()
    assert True, 'Not success'

@pytest.mark.order(2)
def test_parse_hyatt():

    data_path = Path(__file__).parent / 'data' / 'hyatt.json'

    with open(data_path, 'r') as file:
        json_data = json.load(file)

    params = {'location': 'Secrets Moxché Playa del Carmen',
              'region': 'Playa del Carmen',
              'start_date': '2025-02-02',
              'end_date': '2025-02-09',
              'adults': 2,
              'children': 0,
              }

    data = get_standard_data_hyatt(json_data, params)

    assert data.get('currency_prices', None) == 'USD', 'Currency not expected'
    assert data.get('hotel', None) is not None, 'Hotel not found'
    assert data.get('rooms', None) is not None and len(data['rooms']) > 0, 'Rooms not found'
    room = data['rooms'][0]
    assert (room.get('beds', None) and room.get('name') and room.get('price')), 'Room data not found'

    logger.info(f'Result: {data}')