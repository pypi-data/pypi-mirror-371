import json
from pathlib import Path

import pytest
import requests

from scrahot.standard_json import get_standard_data_cvc

base_url = 'http://localhost:5001'


@pytest.mark.order(1)
def test_cvc():

    # url = f'{base_url}/hotel-json-data/cvc.com/Rio Janeiro/Makai Resort All Inclusive/2024-11-23/2024-11-29/3/0'
    # url = f'{base_url}/hotel-json-data/cvc.com/RIO DE JANEIRO/Hotel Nacional Rio de Janeiro/2024-11-29/2024-12-05/2/0'
    # url = f'{base_url}/hotel-json-data/cvc.com/GRAMADO/Hotel Casa da Montanha/2024-11-20/2024-11-26/2/0'
    # url = f'{base_url}/hotel-json-data/cvc.com/MACEIO/Acqua Inn/2025-01-11/2025-01-17/2/0'
    # url = f'{base_url}/hotel-json-data/cvc.com/MACEIO/Wish Natal/2024-10-12/2024-10-18/2/0'
    # url = f'{base_url}/hotel-json-data/cvc.com/undefineasdfd/undefined/2024-09-29/2024-10-05/2/0'
    # url = f'{base_url}/hotel-json-data/cvc.com/Rio de Janeiro/Hotel Nacional Rio de Janeiro/2025-01-11/2025-01-17/2/0'
    # url = f'{base_url}/hotel-json-data/cvc.com/GRAMADO/Buona Vitta Gramado Resort &amp; Spa by Gramado Parks/2025-04-20/2025-04-27/2/0'
    url = f'{base_url}/hotel-json-data/cvc.com/AQUIRAZ/Acqua Beach Park Resort/2025-05-04/2025-05-10/2/0'
    response = requests.get(url)
    assert response.status_code == 200
    data = response.json()
    assert data.get('success', False), f'Not success: {response.json().get("error", None)}'
    assert data.get('currency_prices', None) == 'BRL', 'Currency not expected'
    assert data.get('hotel', None) is not None, 'Hotel not found'
    assert data.get('rooms', None) is not None and len(data['rooms']) > 0, 'Rooms not found'
    room = data['rooms'][0]
    assert (room.get('beds', None) and room.get('name') and room.get('price')), 'Room data not found'

@pytest.mark.order(2)
def test_parse_cvc():

    data_path = Path(__file__).parent / 'data' / 'cvc.json'

    with open(data_path, 'r') as file:
        json_data = json.load(file)

    params = {'location': 'Hotel Refúgio',
              'region': 'MATO',
              'start_date': '2024-12-19',
              'end_date': '2024-12-28',
              'adults': 2,
              'children': 0,
              }

    data = get_standard_data_cvc(json_data, params)

    assert data.get('currency_prices', None) == 'BRL', 'Currency not expected'
    assert data.get('hotel', None) is not None, 'Hotel not found'
    assert data.get('rooms', None) is not None and len(data['rooms']) > 0, 'Rooms not found'
    room = data['rooms'][0]
    assert (room.get('beds', None) and room.get('name') and room.get('price')), 'Room data not found'
