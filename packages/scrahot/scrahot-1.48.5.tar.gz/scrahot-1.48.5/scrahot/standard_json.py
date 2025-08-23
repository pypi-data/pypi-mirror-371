from datetime import datetime, timezone
import traceback


def get_standard_data(data, params):
    """
    Hoteles and Expedia

    """
    response = {
        "success": True,

        "search_criteria": params,

        "hotel": params.get('location'),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
    }

    rooms = []
    for listing in data['data']['propertyOffers']['categorizedListings']:
        # try:
            if listing.get('primarySelections') and len(listing['primarySelections']) > 0:
                property_unit = listing['primarySelections'][0].get('propertyUnit')
                if property_unit:
                    call_to_action = property_unit.get('availabilityCallToAction')
                    if call_to_action:
                        value = call_to_action.get('value')
                        if value and "We are sold out".lower() in value.lower():
                            continue
            room = {}
            header = listing.get('header')
            if header:
                room['name'] = header.get('text')
            else:
                continue

            if listing.get('primarySelections') and len(listing['primarySelections']) > 0:
                property_unit = listing['primarySelections'][0].get('propertyUnit')
                if property_unit and property_unit.get('ratePlans') and len(property_unit['ratePlans']) > 0:
                    payment_policy = property_unit['ratePlans'][0].get('paymentPolicy')
                    if payment_policy and len(payment_policy) > 0 and payment_policy[0].get('price') and \
                            payment_policy[0]['price'].get('displayMessages') and len(
                        payment_policy[0]['price']['displayMessages']) > 0 and \
                            payment_policy[0]['price']['displayMessages'][0].get('lineItems') and len(
                        payment_policy[0]['price']['displayMessages'][0]['lineItems']) > 0:
                        price = payment_policy[0]['price']['displayMessages'][0]['lineItems'][0].get('price')
                        if price:
                            room['price'] = price.get('formatted')

            beds = []
            if listing.get('features'):
                for feature in listing['features']:
                    if feature.get('graphic') and feature['graphic'].get('id') == 'bed':
                        beds.append(feature.get('text'))
                        break

            room['beds'] = beds
            rooms.append(room)
        # except Exception as e:
        #     raise Exception(f"Error getting room data: {e}")

    response['rooms_found'] = rooms.__len__()
    response['currency_prices'] = 'USD'
    response['rooms'] = rooms

    return response


def get_standard_data_second(data, params):
    """
    Despegar, Decolar and BestDay

    """

    response = {
        "success": True,

        "search_criteria": params,

        "hotel": params.get('location'),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
    }

    rooms = []
    if data.get('data') and data['data'].get('has_availability') \
            and data['data'].get('room_groups') and len(data['data']['room_groups']) > 0:

        references = data.get('references')

        room_types = None
        if references and references.get('room_types'):
            room_types = references.get('room_types')

        for listing in data['data']['room_groups']:
            # try:
                if listing.get('room_types') and len(listing['room_types']) > 0:
                    room = {}

                    room_type_id = listing['room_types'][0].get('id')

                    if room_types:
                        room_type = room_types.get(room_type_id)
                        if room_type:
                            room['name'] = room_type.get('name')
                    else:
                        room['name'] = 'N/A'

                    if listing.get('room_packs') and len(listing['room_packs']) > 0:
                        prices = listing['room_packs'][0].get('prices')
                        if prices and prices.get('currency') and prices.get('main'):
                            room['price'] = f"{prices['currency']} {prices['main']}"

                        beds = []
                        bed_options = listing['room_packs'][0].get('bed_options')
                        if bed_options and len(bed_options) > 0:
                            options = bed_options[0].get('options')
                            if options and len(options) > 0 and options[0].get('text'):
                                value = options[0].get('text')
                                beds.append(value)

                        room['beds'] = beds
                        rooms.append(room)
            # except Exception as e:
            #     raise Exception(f"Error getting room data: {e}")

    response['rooms_found'] = rooms.__len__()
    response['currency_prices'] = 'USD'
    response['rooms'] = rooms

    return response


def get_standard_data_booking(data, params, metadata=None):
    """
    Booking

    """
    response = {
        "success": True,

        "search_criteria": params,

        "hotel": params.get('location'),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
    }

    hotel_name = None
    rooms = []
    adults = params.get('persons').get('adults')
    children = params.get('persons').get('children')
    adults = int(adults)
    children = int(children)
    persons = adults
    for listing in data:
        if listing.get('data'):
            #try:
                if not hotel_name:
                    hotel_name = listing['data'].get('b_hotel_name')

                room = {}
                rooms_data = listing['data'].get('rooms')
                if rooms_data and len(rooms_data) > 0:
                    room['name'] = rooms_data[0].get('b_name_gen')

                    # the prices comes from the js object that is loaded from the html
                    # room['price'] =

                    beds = []
                    if rooms_data[0].get('b_bed_type_configuration') and len(rooms_data[0]['b_bed_type_configuration']) > 0:
                        for bed_conf in rooms_data[0]['b_bed_type_configuration']:
                            if bed_conf.get('bed_type') and len(bed_conf['bed_type']) > 0:
                                if bed_conf['bed_type'][0].get('name_withnumber'):
                                    beds.append(bed_conf['bed_type'][0].get('name_withnumber'))

                    best_price = 999999999999.00
                    for room_metadata in metadata['b_rooms_available_and_soldout']:
                        if room_metadata.get('b_name') and room_metadata['b_name'] == room['name']:
                            for block in room_metadata['b_blocks']:
                                if persons <= block['b_max_persons'] and block.get('b_raw_price') and float(block['b_raw_price']) < best_price:
                                    best_price = float(block['b_raw_price'])
                                    room['price'] = block['b_price']
                            break

                    room['beds'] = beds
                    rooms.append(room)
            # except Exception as e:
            #     print(traceback.format_exc())
            #     raise Exception(f"Error getting room data: {e}")

    response['rooms_found'] = rooms.__len__()
    response['currency_prices'] = 'USD'
    response['rooms'] = rooms

    if rooms.__len__() > 0:
        response['hotel'] = hotel_name

    return response


def get_standard_data_cvc(data, params):
    """
    cvc

    """

    response = {
        "success": True,

        "search_criteria": params,

        "hotel": params.get('location'),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
    }

    if data.get('hotel') and data['hotel'].get('rooms') and len(data['hotel']['rooms']) > 0:
        data = data['hotel']
    else:
        data = None

    currency = 'USD'
    rooms = []
    if data:
        # references = data.get('rooms')[0].get('groups')[0]
        #
        # room_types = None
        # if references and references.get('category'):
        #     room_types = references.get('category')

        for listing in data.get('rooms'):
            if listing.get('groups') and len(listing['groups']) > 0:
                listing = listing['groups'][0]
                room = {}

                # room_type_id = listing['room_types'][0].get('id')

                room['name'] = listing.get('name')

                if listing.get('rates') and len(listing['rates']) > 0 and listing['rates'][0].get('currency'):
                    rates = listing['rates'][0]

                    currency = rates['currency']
                    room['price'] = rates.get('priceWithTax')

                if listing.get('description'):
                    beds = []
                    beds.append(listing.get('description'))
                    room['beds'] = beds
                    rooms.append(room)

    response['rooms_found'] = rooms.__len__()
    response['currency_prices'] = currency
    response['rooms'] = rooms

    return response

def get_standard_data_hardrock(data, params):
    """
    hardrock

    """

    response = {
        "success": True,

        "search_criteria": params,

        "hotel": params.get('location'),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
    }

    if data.get('ContentLists') and data['ContentLists'].get('RoomList') and len(data['ContentLists']['RoomList']) > 0:
        data_room = data['ContentLists']
        data_prices = data.get('ProductAvailabilityDetail', {}).get('Prices', [])
    else:
        data_room = None
        data_prices = None

    currency = 'USD'
    rooms = []
    if data_room:

        for room_data in data_room['RoomList']:
            room = {}

            room['name'] = room_data.get('Name')

            prices_info = next((price for price in data_prices
                                if price.get('Product', {}).get('Room', {}).get('Code', '') == room_data.get('Code')), None)


            if prices_info.get('Product', {}).get('Prices', {}).get('Total').get('Price').get('Total'):
                rates = prices_info.get('Product', {}).get('Prices', {}).get('Total').get('Price')

                currency = rates['CurrencyCode']
                room['price'] = rates.get('Total', {}).get('Amount')

            if room_data.get('Details',{}).get('Bedding'):
                beds = []
                bedding = room_data.get("Details", {}).get('Bedding')
                description = (bedding.get('Quantity') + ' '
                               + bedding.get('Type')
                               + f" bed{'s' if int(bedding.get('Quantity')) > 1 else ''}")
                beds.append(description)
                room['beds'] = beds

            rooms.append(room)

    response['rooms_found'] = rooms.__len__()
    response['currency_prices'] = currency
    response['rooms'] = rooms

    return response

def get_standard_data_hyatt(data, params):
    """
    hyatt

    """

    response = {
        "success": True,

        "search_criteria": params,

        "hotel": params.get('location'),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
    }

    if data.get('roomRates') and len(data['roomRates'].items()) > 0:
        data_room = data['roomRates']
    else:
        data_room = None

    currency = 'USD'
    rooms = []
    if data_room:

        for room_code, room_data in data_room.items():
            room = {}

            room['name'] = room_data.get('roomType', {}).get('title')

            rate_plans = room_data.get('ratePlans', [])

            if room_data.get('currencyCode') and len(rate_plans) > 0:
                currency = rate_plans[0].get('currencyCode')
                room['price'] = rate_plans[0].get('totalAfterTax')

            if room_data.get('roomType', {}).get('description'):
                beds = []
                description:str = room_data.get("roomType", {}).get('description')
                description = description.split('.', 1)[0]
                description = description.split('with', 1)[1]
                beds.append(description.strip())
                room['beds'] = beds

            rooms.append(room)

    response['rooms_found'] = rooms.__len__()
    response['currency_prices'] = currency
    response['rooms'] = rooms

    return response


def get_standard_data_palladium(data, params):
    """
    palladium
    """

    response = {
        "success": True,
        "search_criteria": params,
        "hotel": params.get('location'),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
    }

    if data.get('roomData') and len(data['roomData']) > 0:
        data_room = data['roomData']
    else:
        data_room = None

    currency = 'USD'
    rooms = []
    conversion_rate = 1.0  # Default conversion rate

    # Extract conversion rate from currencySelector
    if data.get('currencySelector'):
        for currency_info in data['currencySelector']['currencies']:
            if currency_info['text'] == 'USD':
                conversion_rate = currency_info['conversion']
                break

    if data_room:
        for room_data in data_room:
            room = {}
            room['name'] = room_data.get('parsedRoomData', {}).get('nombre')
            data_prices = room_data.get('parsedRoomData', {}).get('tarifas')

            if room_data.get('currencyCode'):
                # currency = room_data.get('currencyCode')
                price_in_default_currency = room_data.get('parsedRoomData', {}).get('precio_desde')
                room['price'] = round(price_in_default_currency * conversion_rate, 2)

            if room_data.get('parsedRoomData', {}).get('descripcion'):
                beds = []
                beds.append(room_data.get('parsedRoomData', {}).get('descripcion'))
                room['beds'] = beds

            rooms.append(room)

    response['rooms_found'] = rooms.__len__()
    response['currency_prices'] = currency
    response['rooms'] = rooms

    return response