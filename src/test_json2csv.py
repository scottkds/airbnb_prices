import unittest
import pandas as pd
import json
from airbnb_json2csv import load_data, cleaning_fees, room_prices


class TestJson2Csv(unittest.TestCase):

    jd = load_data('/home/scott/projects/mp2/src/json_data.json')

    def test_keys(self):
        jd = self.jd
        print(jd.keys())

    def test_load(self):
        self.assertIsInstance(load_data('/home/scott/projects/mp2/src/json_data.json'), dict)

    def test_priceDataToLists(self):
        jd = self.jd
        cf = cleaning_fees(jd['price'])
        self.assertEqual(cf[0], 5)
        self.assertEqual(len(cf), len(jd['price']))

    def test_RoomPrices(self):
        jd = self.jd
        room_rates = room_prices(jd['rate'])
        self.assertEqual(room_rates[0], 10)
        self.assertEqual(len(room_rates), len(jd['rate']))
        print(json.dumps(jd['rate'][0], indent=4))


if __name__ == '__main__':

    unittest.main()
