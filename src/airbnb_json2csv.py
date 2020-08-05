import pandas as pd
import json
from collections import Counter

def load_data(filename):
    """Loads a json formatted file into a python dict."""
    with open(filename, 'r') as f:
        airbnb_data = json.load(f)
    return airbnb_data

def cleaning_fees(price_data):
    """Retrieves the cleaning fee, if there is one, for each room."""
    cleaning_fees_list = []
    for entry in price_data:
        cleaning_fee = 0
        price_items = entry['priceItems']
        for price in price_items:
            if price['localizedTitle'] == 'Cleaning fee':
                cleaning_fee = price['total']['amount']
        cleaning_fees_list.append(cleaning_fee)

    return cleaning_fees_list

def room_prices(rate_data):
    """Retrieves the room price for each room and returns the list of room
    prices."""
    room_prices = []
    for rate in rate_data:
        room_prices.append(rate['amount'])
    return room_prices

if __name__ == '__main__':

    jd = load_data('/home/scott/projects/mp2/src/json_data.json')

    room_data = {}
    
    # Copy keys and values to a new dictionary. Used cleaning_fees and
    # room_prices to extract those fields from json objects.
    for key, val in jd.items():
        if key == 'price':
            room_data['cleaning_fee'] = cleaning_fees(val)
        elif key == 'rate':
            room_data['price'] = room_prices(val)
        elif key == 'amenityIds':
            pass
        else:
            room_data[key] = val

    # Make sure all the values have the same length.
    for key, val in room_data.items():
        print(key, len(val))

    # Create a dataframe and write it to disk.
    rd = pd.DataFrame(room_data)
    rd.to_csv('/home/scott/projects/mp2/data/room_data.csv', index=False)

    # Get all the possible amenity ids
    amenity_counter = Counter()
    for lst in jd['amenityIds']:
        amenity_counter.update(lst)
    
    # The next couple code blocks are to one-hot encode amenity ids.
    # Create a dictionary with predefined keys and empty list values.
    amenity_ids = sorted(amenity_counter.keys())
    room_amenities = {}
    for id in amenity_ids:
        room_amenities[id] = []

    # Loop through each list of amenity ids. Update each rooms_amenities['id'] with 1
    # remove the id from the set of amentiy ids. For any id remaining in the
    # set update the room_amenities['id'] with 0
    for item in jd['amenityIds']:
        ids = set(amenity_ids)
        for id in item:
            room_amenities[id].append(1)
            ids.remove(id)
        for id in ids:
            room_amenities[id].append(0)

    # Add key, value pair for the airbnb room id.
    room_amenities['id'] = jd['id']

    # Validate the number of rows is correct.
    for key, value in room_amenities.items():
        assert len(val) == len(jd['amenityIds'])

    # Create a dataframe of amenities and write it to disk.
    ra = pd.DataFrame(room_amenities)
    ra.to_csv('/home/scott/projects/mp2/data/room_amenities.csv', index=False)
        


    
