# Recursively searches a dictionary for a key. Returns the value for the first
# key it finds.

import unittest

def find_key(dic, search_key):
    """REcursively searches a dictionary for the 'search_key'. If it is found
    then the value of 'search_key' returned. If it is not found returns None."""
    value = None
    def find_key_list(lst, search_key):
        for item in lst:
            if isinstance(item, list) or isinstance(item, tuple):
                value = find_key_list(item, search_key)
                if value:
                    return value
            elif isinstance(item, dict):
                value = find_key(item, search_key)
                if value:
                    return value
        return value

    if search_key in dic:
        return dic[search_key]
    else:
        keys = dic.keys()
        for key in keys:
            if isinstance(dic[key], dict):
                return find_key(dic[key], search_key)
            elif isinstance(dic[key], list):
                value =  find_key_list(dic[key], search_key)
                if value:
                    return value
    return None

class TestFindKey(unittest.TestCase):

    def test_findKey(self):
        d1 = {1:1}
        d2 = {1: 1, 2: {3: 'three'}}
        d3 = {1: [{2:2}, [3, 4, 5, {6: [7, 8, 9, {12: 'twelve'}]}]]}
        d4 = {1: 2, 3: {4: 4}, 5: {6: 6}}
        d5 = {1: [3, 4, 5, {6: [7, 8, 9, {12: 'twelve'}]}], 2: {3: 4}}
        self.assertEqual(find_key(d1, 1), 1)
        self.assertEqual(find_key(d2, 3), 'three')
        self.assertEqual(find_key(d3, 12), 'twelve')
        self.assertIsNone(find_key(d3, 13))
        self.assertEqual(find_key(d4, 4), 4)
        self.assertEqual(find_key(d4, 5), {6: 6})
        self.assertEqual(find_key(d5, 3), 4)

if __name__ == '__main__':

    unittest.main()

