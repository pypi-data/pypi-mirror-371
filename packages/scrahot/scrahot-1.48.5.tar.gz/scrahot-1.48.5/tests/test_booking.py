import pytest
import requests


base_url = 'http://localhost:5005'


@pytest.mark.order(1)
def test_booking():

    # url = f'{base_url}/hotel-json-data/booking.com/All Ritmo Cancun Resort & Water Park/2024-11-03/2024-11-09/2/0'
    # url = f'{base_url}/hotel-json-data/booking.com/Hotel Guadalajara Plaza Ejecutivo/2025-02-23/2025-03-01/2/0'
    # url = f'{base_url}/hotel-json-data/booking.com/AC Hotel by Marriott San Juan Condado/2025-02-06/2025-02-12/2/0'
    url = f'{base_url}/hotel-json-data/booking.com/Jacuzzi Ocean View/2025-07-06/2025-07-11/2/0'
    # url = f'{base_url}/hotel-json-data/booking.com/Beachscape Kin ha Villas & Suites/2025-1-18/2025-1-25/2/0'
    response = requests.get(url)
    assert response.status_code == 200
    data = response.json()
    assert data.get('success', False), f'Not success: {response.json().get("error", None)}'
    assert data.get('currency_prices', None) == 'USD', 'Currency not expected'
    assert data.get('hotel', None) is not None, 'Hotel not found'
    assert data.get('rooms', None) is not None and len(data['rooms']) > 0, 'Rooms not found'
    room = data['rooms'][0]
    assert (room.get('beds', None) and room.get('name') and room.get('price')), 'Room data not found'
