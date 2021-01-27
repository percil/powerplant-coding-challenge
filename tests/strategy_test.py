import unittest

from services.strategy import *
from domain.engie_objects import *


class StrategyComputeSinglePowerPlantTestCase(unittest.TestCase):

    def test_max_available_power(self):
        # test max available power
        test_result = compute_single_power_plant(
            ProcessResult(
                type="gasfired",
                name="test_01",
                available_power=50,
                minimum_power=10),
            100, False)

        self.assertEqual(test_result.dispatched_power, 50)

    def test_less_than_available_power(self):
        # test with load lower than available_power
        test_result = compute_single_power_plant(
            ProcessResult(type="gasfired",
                          name="test_02",
                          available_power=50,
                          minimum_power=10),
            25, False)

        self.assertEqual(test_result.dispatched_power, 25)

    def test_less_than_minimum_power(self):
        # test with load lower than min_power
        test_result = compute_single_power_plant(
            ProcessResult(
                type="gasfired",
                name="test_03",
                available_power=50,
                minimum_power=10),
            5, False)

        self.assertEqual(test_result.dispatched_power, 0)

    def test_with_average(self):
        # test with avg
        test_result = compute_single_power_plant(
            ProcessResult(
                type="gasfired",
                name="test_04",
                available_power=50,
                minimum_power=30),
            100, True)

        self.assertEqual(test_result.dispatched_power, 40)


class StrategyComputePowerPlantDuetTestCase(unittest.TestCase):

    @staticmethod
    def sum_dispatched_power(results: [ProcessResult]) -> int:
        sum_dispatched = 0

        for result in results:
            sum_dispatched += result.dispatched_power

        return sum_dispatched

    def test_max_available_power(self):
        # test max available power
        test_result = compute_power_plant_duet(
            ProcessResult(
                type="gasfired",
                name="test_01",
                available_power=50,
                minimum_power=10),
            ProcessResult(
                type="gasfired",
                name="test_02",
                available_power=50,
                minimum_power=10),
            100)

        self.assertEqual(self.sum_dispatched_power(test_result), 100)

    def test_less_than_available_power(self):
        # test with load lower than available_power
        test_result = compute_power_plant_duet(
            ProcessResult(
                type="gasfired",
                name="test_01",
                available_power=50,
                minimum_power=10),
            ProcessResult(
                type="gasfired",
                name="test_02",
                available_power=50,
                minimum_power=10),
            75)

        self.assertEqual(self.sum_dispatched_power(test_result), 75)

    def test_less_than_available_power_once(self):
        # test with load lower than available_power
        test_result = compute_power_plant_duet(
            ProcessResult(
                type="gasfired",
                name="test_01",
                available_power=50,
                minimum_power=10),
            ProcessResult(
                type="gasfired",
                name="test_02",
                available_power=50,
                minimum_power=10),
            15)

        self.assertEqual(self.sum_dispatched_power(test_result), 15)

    def test_less_than_minimum_power(self):
        # test with load lower than available_power
        test_result = compute_power_plant_duet(
            ProcessResult(
                type="gasfired",
                name="test_01",
                available_power=50,
                minimum_power=10),
            ProcessResult(
                type="gasfired",
                name="test_02",
                available_power=50,
                minimum_power=10),
            5)

        self.assertEqual(self.sum_dispatched_power(test_result), 0)


class StrategyPriceComputingTestCase(unittest.TestCase):

    @staticmethod
    def get_fuels() -> List[Fuel]:
        raw_fuels = {
            "gas(euro/MWh)": 10,
            "kerosine(euro/MWh)": 50,
            "co2(euro/ton)": 20,
            "wind(%)": 60
        }
        fuels = []
        for fuel_str in raw_fuels:
            fuels.append(Fuel(fuel_str, raw_fuels[fuel_str]))

        return fuels

    def setUp(self) -> None:
        self.orchestrator = StrategyOrchestrator()

    def test_turbojet_strategy(self):
        turbojet = PowerPlant(**{
            "name": "tj1",
            "type": "turbojet",
            "efficiency": 0.5,
            "pmin": 0,
            "pmax": 16
        })
        power_plant = EnrichedPowerPlant(turbojet, self.get_fuels())
        result = self.orchestrator.process_power_plant(power_plant)

        self.assertEqual(result.cost, 100)
        self.assertTrue(result.order > 100)

    def test_gas_fired_strategy(self):
        gas_fired = PowerPlant(**{
            "name": "gasfiredbig1",
            "type": "gasfired",
            "efficiency": 0.50,
            "pmin": 100,
            "pmax": 460
        })

        power_plant = EnrichedPowerPlant(gas_fired, self.get_fuels())
        result = self.orchestrator.process_power_plant(power_plant)

        self.assertEqual(result.cost, 20)
        self.assertTrue(10 < result.order < 100)

    def test_wind_turbine_strategy(self):
        wind_turbine = PowerPlant(**{
            "name": "windpark1",
            "type": "windturbine",
            "efficiency": 1,
            "pmin": 0,
            "pmax": 150
        })

        power_plant = EnrichedPowerPlant(wind_turbine, self.get_fuels())
        result = self.orchestrator.process_power_plant(power_plant)

        self.assertEqual(result.cost, 0)
        self.assertTrue(result.order < 0)


if __name__ == '__main__':
    unittest.main()
