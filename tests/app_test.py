from app.app import *
from domain_test import *


class AppTestCase(unittest.TestCase):
    @staticmethod
    def sum_p(results: [ResponseEntry]) -> int:
        """
        Sums all the 'p' variables from the results.
        :param results: the result entries
        :return: the sum of all 'p'
        """
        p_sum = 0
        for result in results:
            p_sum += result.p
        return p_sum

    def setUp(self) -> None:
        try:
            self.payload: Payload = load_json('tests/fixtures/payload1.json')
        except:
            print("Loading tests from IDE, using another path")
            self.payload: Payload = load_json('fixtures/payload1.json')

    def test_production_plan(self):
        # Call the tested function
        response = production_plan(self.payload)
        # Validate that we have a response
        self.assertIsNotNone(response)
        # Validate that we have the same amount of response entries as power plants
        self.assertEqual(len(response), len(self.payload.powerplants))
        # Validate the the total power of the response matches the requested load
        self.assertEqual(self.sum_p(response), self.payload.load * 10)


if __name__ == '__main__':
    unittest.main()
