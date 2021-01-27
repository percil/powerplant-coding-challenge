from typing import List, Optional
from pydantic import BaseModel

GAS_FIRED = 'gasfired'
TURBOJET = 'turbojet'
WIND_TURBINE = 'windturbine'


class RawFuel:
    """
    Internal objects used for matching fuel with power plant type.
    """

    def __init__(self, type: str, content: list):
        self._type = type
        self._content = content

    @property
    def content(self):
        return self._content

    @property
    def type(self):
        return self._type


FUELS = [
    RawFuel(GAS_FIRED, ['gas']),
    RawFuel(TURBOJET, ['kerosine']),
    RawFuel(WIND_TURBINE, ['wind'])
]


class PowerPlant(BaseModel):
    """
    Class defining a power plant as expected in the payload
    """
    name: str
    type: str
    efficiency: float
    pmin: int
    pmax: int

    def is_gas_fired(self) -> bool:
        return GAS_FIRED == self.type

    def is_turbojet(self) -> bool:
        return TURBOJET == self.type

    def is_wind_turbine(self) -> bool:
        return WIND_TURBINE == self.type

    @property
    def raw_fuels(self) -> Optional[list]:
        for fuel in FUELS:
            if self.type == fuel.type:
                return fuel.content
        return None


class Fuel:
    """
    Class defining a fuel entry as expected in the payload
    """

    def __init__(self, name, data):
        self._name = name
        self._data = data

    @property
    def name(self) -> str:
        return self._name

    @property
    def data(self) -> float:
        return self._data


class EnrichedPowerPlant:
    """
    Class defining an enriched power plant. Such item is composed by the main PowerPlant instance and the list of
    matching fuels.
    """

    def __init__(self, base_power_plant: PowerPlant, incoming_fuels: List[Fuel]):
        self._base = base_power_plant
        self._fuels = []

        for fuel in incoming_fuels:
            for supportedFuel in base_power_plant.raw_fuels:
                if supportedFuel in fuel.name:
                    self._fuels.append(fuel)

    @property
    def base(self) -> PowerPlant:
        return self._base

    @property
    def fuels(self) -> List[Fuel]:
        return self._fuels


class Payload(BaseModel):
    """
    Class defining the expected payload (or request body).
    """
    load: int
    fuels: dict
    powerplants: List[PowerPlant]


class ResponseEntry:
    """
    Class defining an entry for the response.
    """

    def __init__(self, name, p):
        self.name = name
        self.p = p
