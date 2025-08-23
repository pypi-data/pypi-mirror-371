from typing import TYPE_CHECKING

import openapi
from openapi.api.carbon_free_energy_api import CarbonFreeEnergyAPI
from openapi.api.carbon_intensity_api import CarbonIntensityAPI
from openapi.api.net_load_api import NetLoadAPI
from openapi.api.power_breakdown_api import PowerBreakdownAPI
from openapi.api.price_day_ahead_api import PriceDayAheadAPI
from openapi.api.renewable_energy_api import RenewableEnergyAPI
from openapi.api.total_load_api import TotalLoadAPI

from .adapters import (
    CarbonFreeEnergyAdapter,
    CarbonIntensityAdapter,
    NetLoadAdapter,
    PowerBreakdownAdapter,
    PriceDayAheadAdapter,
    RenewableEnergyAdapter,
    TotalLoadAdapter,
)
from .config import HOST

if TYPE_CHECKING:
    pass


class ElectricityMapsClient:
    """Enhanced Electricity Maps client with user-friendly API."""

    def __init__(self, api_client):
        self._api_client = api_client
        # self.api = DefaultAdapter(DefaultAPI(api_client)) # needs to be fixed
        # self.optimize = OptimizeAdapter(DefaultAPI(api_client)) # needs to be fixed
        self.carbon_intensity = CarbonIntensityAdapter(CarbonIntensityAPI(api_client))
        self.carbon_free_energy = CarbonFreeEnergyAdapter(
            CarbonFreeEnergyAPI(api_client)
        )
        self.net_load = NetLoadAdapter(NetLoadAPI(api_client))
        self.power_breakdown = PowerBreakdownAdapter(PowerBreakdownAPI(api_client))
        self.price_day_ahead = PriceDayAheadAdapter(PriceDayAheadAPI(api_client))
        self.renewable_energy = RenewableEnergyAdapter(RenewableEnergyAPI(api_client))
        self.total_load = TotalLoadAdapter(TotalLoadAPI(api_client))

    def __getattr__(self, name):
        """Delegate unknown attributes to the underlying API client."""
        return getattr(self.api, name)


def create_client(api_key: str) -> ElectricityMapsClient:
    """
    Create a configured Electricity Maps API client.

    This function eliminates the boilerplate configuration required by the OpenAPI client
    and returns a fully configured ElectricityMapsClient instance with enhanced API.

    Args:
        api_key: Your Electricity Maps API key
        host: API host URL (defaults to production)

    Returns:
        A configured ElectricityMapsClient instance with enhanced API and full type support
    """
    configuration = openapi.Configuration(host=HOST)
    configuration.api_key["authToken"] = api_key

    api_client = openapi.ApiClient(configuration)
    return ElectricityMapsClient(api_client)
