import pytest
import requests


base_url = 'http://localhost:5001'


@pytest.mark.order(1)
def test_bestday():

    # url = f'{base_url}/hotel-json-data/bestday.com.mx/All Ritmo Cancun Resort & Water Park/2024-10-03/2024-10-09/2/0'
    # url = f'{base_url}/hotel-json-data/bestday.com.mx/All Ritmo Cancun Resort & Water Park/2024-10-18/2024-10-24/2/0'
    url = f'{base_url}/hotel-json-data/bestday.com.mx/Beachscape Kin ha Villas & Suites/2024-11-18/2024-11-21/2/0'
    response = requests.get(url)
    assert response.status_code == 200
    data = response.json()
    assert data.get('success', False), f'Not success: {response.json().get("error", None)}'
    assert data.get('currency_prices', None) == 'USD', 'Currency not expected'
    assert data.get('hotel', None) is not None, 'Hotel not found'
    assert data.get('rooms', None) is not None and len(data['rooms']) > 0, 'Rooms not found'
    room = data['rooms'][0]
    assert (room.get('beds', None) and room.get('name') and room.get('price')), 'Room data not found'
