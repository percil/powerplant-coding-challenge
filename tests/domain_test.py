import json
import unittest

from domain.engie_objects import *


def load_json(file: str) -> Payload:
    """
    Loads the file having the provided name into a Payload object.
    :param file: the JSON file.
    :return: the payload
    """
    # open the file
    with open(file) as json_file:
        # reads it
        data = json.load(json_file)

    # init the Payload object with the read data
    payload = Payload(**data)
    # job done
    return payload


class DomainTestCase(unittest.TestCase):

    def setUp(self) -> None:
        try:
            self.payload: Payload = load_json('tests/fixtures/payload1.json')
        except:
            print("Loading tests from IDE, using another path")
            self.payload: Payload = load_json('fixtures/payload1.json')

    def test_load(self):
        # Test the load itself
        self.assertIsNotNone(self.payload)

    def test_content(self):
        # Test the loaded values
        self.assertEqual(self.payload.load, 480)
        self.assertEqual(len(self.payload.fuels), 4)
        self.assertEqual(len(self.payload.powerplants), 6)


if __name__ == '__main__':
    unittest.main()
