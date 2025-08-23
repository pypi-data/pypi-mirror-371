import json
from pathlib import Path

import pytest
import requests
from loguru import logger

from scrahot.standard_json import get_standard_data_palladium

base_url = 'http://localhost:5001'


@pytest.mark.order(1)
def test_palladium():

    # url = f'{base_url}/hotel-json-data/palladium.com/Mexico/Grand Palladium Vallarta Resort & Spa/2025-01-13/2025-01-19/2/0'
    url = f'{base_url}/hotel-json-data/palladium.com/Mexico/Grand Palladium Select Costa Mujeres/2025-01-12/2025-01-18/2/0'
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
def test_parse_palladium():

    data_path = Path(__file__).parent / 'data' / 'palladiumv2.json'

    with open(data_path, 'r') as file:
        json_data = json.load(file)

    params = {'location': 'Grand Palladium Costa Mujeres Resort & Spa',
              'region': 'Costa Mujeres',
              'start_date': '2025-01-06',
              'end_date': '2025-01-13',
              'adults': 2,
              'children': 0,
              }

    data = get_standard_data_palladium(json_data, params)

    assert data.get('currency_prices', None) == 'USD', 'Currency not expected'
    assert data.get('hotel', None) is not None, 'Hotel not found'
    assert data.get('rooms', None) is not None and len(data['rooms']) > 0, 'Rooms not found'
    room = data['rooms'][0]
    assert (room.get('beds', None) and room.get('name') and room.get('price')), 'Room data not found'

    logger.info(f'Result: {data}')
