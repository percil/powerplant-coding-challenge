from __future__ import annotations
from abc import ABC, abstractmethod

from domain.engie_objects import EnrichedPowerPlant


class ProcessResult:
    """
    This class represents an intermediary object containing all the information needed in order to dispatch power
    across the power plants.
    """

    def __init__(self, type: str, name: str, available_power: int, minimum_power: int, order: int = None,
                 cost: float = None, dispatched_power: int = 0):
        self._order = order
        self._type = type
        self._name = name
        self._available_power = available_power
        self._minimum_power = minimum_power
        self._cost = cost
        self._dispatched_power = dispatched_power

    @property
    def order(self) -> int:
        return self._order

    @order.setter
    def order(self, value):
        self._order = value

    @property
    def type(self) -> str:
        return self._type

    @property
    def name(self) -> int:
        return self._name

    @property
    def available_power(self) -> int:
        return self._available_power

    @available_power.setter
    def available_power(self, value: int) -> None:
        self._available_power = value

    @property
    def minimum_power(self) -> int:
        return self._minimum_power

    @property
    def cost(self) -> float:
        return self._cost

    @cost.setter
    def cost(self, value: float) -> None:
        self._cost = value

    @property
    def dispatched_power(self) -> int:
        return self._dispatched_power

    @dispatched_power.setter
    def dispatched_power(self, dispatched_power: int) -> None:
        self._dispatched_power = dispatched_power


class StrategyOrchestrator:
    """
    Orchestrator for the ranking strategy.
    """

    def __init__(self) -> None:
        self._wind_turbine_strategy = WindTurbineStrategy()
        self._gas_fired_strategy = GasFiredStrategy()
        self._turbojet_strategy = TurbojetStrategy()

    def process_power_plant(self, power_plant: EnrichedPowerPlant) -> ProcessResult:
        """
        Processes the provided enriched power plant by calling the right strategy (based on the power plant type).
        :param power_plant: the enriched power plant.
        :return: the intermediate process result containing cost and order.
        """
        if power_plant.base.is_gas_fired():
            return self._gas_fired_strategy.compute(power_plant)
        if power_plant.base.is_turbojet():
            return self._turbojet_strategy.compute(power_plant)
        if power_plant.base.is_wind_turbine():
            return self._wind_turbine_strategy.compute(power_plant)


class Strategy(ABC):
    """
    Abstract class use by each ranking strategy specification.
    """

    @abstractmethod
    def compute(self, power_plant: EnrichedPowerPlant) -> ProcessResult:
        """
        The main function for converting the provided enriched power plant into intermediate process result.
        :param power_plant: the enriched power plant.
        :return: the intermediate process result.
        """
        pass

    @staticmethod
    def pre_process(power_plant: EnrichedPowerPlant) -> ProcessResult:
        """
        Pre-processing function common to GasFiredStrategy and TurbojetStrategy.
        :param power_plant: the enriched power plant.
        :return: the pre-intermediate process result.
        """

        cost = 0.0

        # Instantiate the result based on the enriched power plant
        result = ProcessResult(name=power_plant.base.name,
                               type=power_plant.base.type,
                               available_power=power_plant.base.pmax * 10,
                               minimum_power=power_plant.base.pmin * 10)

        # Calculate the cost based on the fuel price and the power plant efficiency
        if len(power_plant.fuels) == 1:
            cost = power_plant.fuels[0].data / power_plant.base.efficiency

        result.cost = cost

        return result


class WindTurbineStrategy(Strategy):
    """
    Ranking strategy for wind turbine power plant.
    """

    def compute(self, power_plant: EnrichedPowerPlant) -> ProcessResult:
        available_power = 0

        # Instantiate the result based on the enriched power plant
        result = ProcessResult(name=power_plant.base.name,
                               type=power_plant.base.type,
                               available_power=0,
                               minimum_power=power_plant.base.pmin * 10,
                               cost=0.0)

        # Calculate the available power based on the wind forecast
        if len(power_plant.fuels) == 1:
            available_power += int((power_plant.base.pmax / 100 * power_plant.fuels[0].data) * 10)
        result.available_power = available_power

        # Define an arbitrary (1 for great ranking) order including the available power
        result.order = 1 - result.available_power

        return result


class TurbojetStrategy(Strategy):
    """
    Ranking strategy for turbojet power plant.
    """

    def compute(self, power_plant: EnrichedPowerPlant) -> ProcessResult:
        result = super(TurbojetStrategy, self).pre_process(power_plant)

        # Define an arbitrary (100 for poor ranking) order including the cost of power
        result.order = 100 + result.cost

        return result


class GasFiredStrategy(Strategy):
    """
    Ranking strategy for gas fired power plant.
    """

    def compute(self, power_plant: EnrichedPowerPlant) -> ProcessResult:
        result = super(GasFiredStrategy, self).pre_process(power_plant)

        # Define an arbitrary (10 for middle ranking) order including the cost of power
        result.order = 10 + result.cost

        return result


def average(left: int, right: int) -> int:
    """
    Utility function calculating the average of two integers.
    :param left: the left integer.
    :param right: the right integer.
    :return: the average.
    """
    return int((left + right) / 2)


def compute_single_power_plant(result: ProcessResult, load: int, use_avg: bool = False) -> ProcessResult:
    """
    Fill the dispatched power of a single process result based on the provided load. The average of minimum and
    available power can be requested.
    :param result: the intermediate result.
    :param load: the load.
    :param use_avg: if the average has to be used.
    :return: the completed process result.
    """

    if use_avg:
        # Just use the average. Straight. We don't care about the load. YOLO.
        result.dispatched_power = average(result.minimum_power, result.available_power)
    else:
        # Use the load value if its value is between the minimum and the available power.
        if result.minimum_power < load < result.available_power:
            result.dispatched_power = load
        # Use the maximum power if the load is greater than what the power plant can deliver.
        elif load > result.available_power:
            result.dispatched_power = result.available_power
            pass

    return result


def compute_power_plant_duet(left_result: ProcessResult, right_result: ProcessResult, load: int) -> [ProcessResult]:
    """
    Fill the dispatched power of a pair of power plants based on the provided load.
    :param left_result: the first intermediate result.
    :param right_result: the second intermediate result.
    :param load: the load.
    :return: a list of the completed process results.
    """

    to_return = []

    # Gather all the available power
    available_power = left_result.available_power + right_result.available_power
    # Gather the already dispatched power
    dispatched_power = left_result.dispatched_power + right_result.dispatched_power
    # Find the minimum power
    minimum_power = min(left_result.minimum_power, right_result.minimum_power)

    print(
        f'[start] Left dispatched: {left_result.dispatched_power} | Right dispatched: {right_result.dispatched_power} |'
        f' Total dispatched: {left_result.dispatched_power + right_result.dispatched_power}')

    # Check if the load is greater than the minimum power and if there's already some power dispatched
    if dispatched_power == 0 and load >= minimum_power:
        # If the load is greater than all the available power, use everything
        if load >= available_power:
            left_result.dispatched_power = left_result.available_power
            right_result.dispatched_power = right_result.available_power
        # Otherwise dispatch the power between both power plants
        elif load < available_power:
            # Give a try dispatching on a single power plant
            temp_left_result = compute_single_power_plant(left_result, load)
            remaining_power = load - temp_left_result.dispatched_power
            # Check if some power remains in the expected load
            if remaining_power > 0:
                # If so, check if the remaining power is lower than the second power plant's minimum power
                if remaining_power < right_result.minimum_power:
                    # If so, give a try using average power on the first power plant
                    temp_left_result = compute_single_power_plant(left_result, load, True)
                    # Then check if the remaining power is still lower than the second power plant's minimum power
                    if (load - temp_left_result.dispatched_power) < right_result.minimum_power:
                        # If so, use average on both
                        left_result = compute_single_power_plant(left_result, int((load + 1) / 2))
                        right_result = compute_single_power_plant(right_result, int(load / 2))
                    # So far, so good. Let's dispatch remaining load on the second power plant
                    else:
                        right_result = compute_single_power_plant(right_result, (load - left_result.dispatched_power))
                # First try award: let's dispatch accordingly
                else:
                    left_result = temp_left_result
                    right_result = compute_single_power_plant(right_result, (load - left_result.dispatched_power))
    # The last chance possibility to dispatch the power
    else:
        if right_result.dispatched_power == 0 and right_result.available_power > load > right_result.minimum_power:
            right_result.dispatched_power = load

    print(
        f'[end] Left dispatched: {left_result.dispatched_power} | Right dispatched: {right_result.dispatched_power} | '
        f'Total dispatched: {left_result.dispatched_power + right_result.dispatched_power}')

    # Put the process results in the list. Obviously.
    to_return.append(left_result)
    to_return.append(right_result)

    # Job done.
    return to_return


class PowerDispatcher(ABC):
    """
    Abstract class for dispatching power based on the intermediate process results.
    """

    @abstractmethod
    def compute(self, results: [ProcessResult], load: int) -> [ProcessResult]:
        """
        The main function for enriching provided process results with dispatched power.
        :param results: the intermediate process results.
        :param load: the load to dispatch.
        :return: the completed process results.
        """
        pass


class GasFiredDispatcher(PowerDispatcher):
    """
    Power dispatcher for gas fired power plants. Which are a bit more complex than the 'simple' ones.
    """

    def compute(self, results: [ProcessResult], load: int) -> [ProcessResult]:
        to_return = []

        # Depending on the count of process results, let's call our utility functions
        # If we have only one process result to deal with
        if len(results) == 1:
            # It's pretty easy, don't you agree?
            to_return.append(compute_single_power_plant(results[0], load))
        # If we have only two process results to deal with
        elif len(results) == 2:
            # It's no rocket science neither, let's proceed then
            to_return = compute_power_plant_duet(results[0], results[1], load)
        # Now, we're talking
        elif len(results) > 2:
            i = 1
            remaining_power = load
            # Prepare the first result to pass to the utility function
            previous_result = results[0]
            first_call = True

            # Loop while power still has to be dispatched and we still have elements to process
            while i < len(results) and remaining_power > 0:
                # Assign the second result
                current_result = results[i]
                i += 1

                # Give a try
                temp_results = compute_power_plant_duet(previous_result, current_result, remaining_power)
                # Align the remaining power load
                for temp_result in temp_results:
                    if not first_call:
                        remaining_power += previous_result.dispatched_power
                    remaining_power -= temp_result.dispatched_power

                if first_call:
                    first_call = False

                to_return.append(temp_results[0])
                previous_result = temp_results[1]

                # If we are on the last element, let's add the current one
                if i == len(results):
                    to_return.append(temp_results[1])

            # Validate if we have the same count and the same entries in and out
            if len(to_return) < len(results):
                # If you're still reading all my comments, I gotta make you understand that
                for in_result in results:
                    # I'll never gonna give you up
                    found = False
                    # Never gonna let you down
                    for out_result in to_return:
                        # Never gonna run around and desert you
                        if in_result.name == out_result.name:
                            # Never gonna make you cry
                            found = True
                            # Never gonna say goodbye
                            continue
                    # Never gonna tell a lie
                    if not found:
                        # And hurt you
                        to_return.append(in_result)

        # Here the list is empty...
        else:
            to_return = results

        return to_return


class SimplePowerDispatcher(PowerDispatcher):
    """
    Power dispatcher for 'simple' power plants (in this case: wind turbine and turbojet)
    """

    def compute(self, results: [ProcessResult], load: int) -> [ProcessResult]:
        processed_results = []
        remaining_load = load

        # Loop on the process results
        for result in results:
            # If there's still power to dispatch
            if remaining_load > 0:
                # If the the load is greater than available power
                if remaining_load > result.available_power:
                    # UNLEASH THE WHOLE POWER!
                    result.dispatched_power = result.available_power
                    remaining_load -= result.dispatched_power
                # Otherwise, try to play it a bit smarter
                elif result.available_power > remaining_load > result.minimum_power:
                    result.dispatched_power = remaining_load
                    remaining_load = 0

            # In each and every case, just 'flag' the result as processed
            processed_results.append(result)

        # Job done.
        return processed_results
