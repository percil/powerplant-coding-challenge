from fastapi import FastAPI

import uvicorn

from domain.engie_objects import *
from services.strategy import *

app = FastAPI()

orchestrator = StrategyOrchestrator()

simple_dispatcher = SimplePowerDispatcher()
gas_fired_dispatcher = GasFiredDispatcher()


@app.post("/productionplan")
def production_plan(payload: Payload) -> [ResponseEntry]:
    """
    REST endpoint accepting POST requests where the request body accepts a well-formatted payload.
    :param payload: the payload
    :return: a list of ResponseEntry
    """

    # Parse the fuels dict as Fuel objects
    fuels = []
    for fuel_str in payload.fuels:
        fuels.append(Fuel(fuel_str, payload.fuels[fuel_str]))

    results = []
    the_response = []

    # Loop on power plants (enriched with parsed fuels) to discover both costs and order
    # This is based on a simple implementation of the merit order ranking concept
    for power_plant in payload.powerplants:
        process_result = orchestrator.process_power_plant(EnrichedPowerPlant(power_plant, fuels))
        results.append(process_result)

    # Sort the result based on the computed order
    results.sort(key=lambda r: r.order, reverse=False)
    # Align the remaining load with the expected output unit
    remaining_load = payload.load * 10

    wind_turbine_results = []
    gas_fired_results = []
    turbojet_results = []

    # Distribute the results based on the power plant types
    for result in results:
        if GAS_FIRED == result.type:
            gas_fired_results.append(result)
        elif WIND_TURBINE == result.type:
            wind_turbine_results.append(result)
        elif TURBOJET == result.type:
            turbojet_results.append(result)

    # Start with the wind turbine for dispatching power load by plant
    for result in simple_dispatcher.compute(wind_turbine_results, remaining_load):
        remaining_load -= result.dispatched_power
        the_response.append(ResponseEntry(result.name, result.dispatched_power))

    # Continue with the gas fired for dispatching power load by plant
    for result in gas_fired_dispatcher.compute(gas_fired_results, remaining_load):
        remaining_load -= result.dispatched_power
        the_response.append(ResponseEntry(result.name, result.dispatched_power))

    # End with the turbojet for dispatching power load by plant
    for result in simple_dispatcher.compute(turbojet_results, remaining_load):
        remaining_load -= result.dispatched_power
        the_response.append(ResponseEntry(result.name, result.dispatched_power))

    # A quick validation verifying that the response load matches the requested one
    response_load = 0
    for item in the_response:
        response_load += item.p

    # With a pretty print in the console
    print(
        f'Expected load: {payload.load * 10} | Response load: {response_load} -> {payload.load * 10 == response_load}')

    # Job done. Cheerio.
    return the_response


if __name__ == "__main__":
    """
    Entry point of the application
    """
    uvicorn.run(app, host="0.0.0.0", port=8888)
