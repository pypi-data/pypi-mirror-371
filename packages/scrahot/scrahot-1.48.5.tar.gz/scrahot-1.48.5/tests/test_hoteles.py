import pytest
import requests


base_url = 'http://localhost:5001'


@pytest.mark.order(1)
def test_hoteles():

    # url = f'{base_url}/hotel-json-data/hoteles.com/Hotel Xcaret/2024-11-23/2024-11-29/3/1'
    url = f'{base_url}/hotel-json-data/hoteles.com/Garden View/2025-08-17/2025-08-22/2/0'
    response = requests.get(url)
    assert response.status_code == 200
    data = response.json()
    assert data.get('success', False), f'Not success: {response.json().get("error", None)}'
    assert data.get('currency_prices', None) == 'USD', 'Currency not expected'
    assert data.get('hotel', None) is not None, 'Hotel not found'
    assert data.get('rooms', None) is not None and len(data['rooms']) > 0, 'Rooms not found'
    room = data['rooms'][0]
    assert (room.get('beds', None) and room.get('name') and room.get('price')), 'Room data not found'
