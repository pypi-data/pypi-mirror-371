from openapi.api.carbon_free_energy_api import CarbonFreeEnergyAPI
from openapi.models.energy_share import EnergyShare
from openapi.models.history_response_energy_share import HistoryResponseEnergyShare
from openapi.models.temporal_granularity import TemporalGranularity


class CarbonFreeEnergyAdapter:
    """Carbon free energy API methods with simplified interface."""

    def __init__(self, api: CarbonFreeEnergyAPI):
        self._api = api

    def latest(
        self,
        zone_key: str | None = None,
        lon: int | None = None,
        lat: int | None = None,
        disable_caller_lookup: bool | None = None,
        data_center_provider: str | None = None,
        data_center_region: str | None = None,
        temporal_granularity: TemporalGranularity | None = None,
    ) -> EnergyShare:
        """Get the latest carbon free energy for a zone or coordinates."""
        return self._api.get_carbon_free_energy_latest(
            zone_key=zone_key,
            lon=lon,
            lat=lat,
            disable_caller_lookup=disable_caller_lookup,
            data_center_provider=data_center_provider,
            data_center_region=data_center_region,
            temporal_granularity=temporal_granularity,
        )

    def history(
        self,
        zone_key: str | None = None,
        lon: int | None = None,
        lat: int | None = None,
        disable_caller_lookup: bool | None = None,
        data_center_provider: str | None = None,
        data_center_region: str | None = None,
        temporal_granularity: TemporalGranularity | None = None,
    ) -> HistoryResponseEnergyShare:
        """Get the carbon free energy history for a zone or coordinates."""
        return self._api.get_carbon_free_energy_history(
            zone_key=zone_key,
            lon=lon,
            lat=lat,
            disable_caller_lookup=disable_caller_lookup,
            data_center_provider=data_center_provider,
            data_center_region=data_center_region,
            temporal_granularity=temporal_granularity,
        )

    # Currently broken with response
    # def past(
    #     self,
    #     dt: str,
    #     zone_key: str | None = None,
    #     lon: int | None = None,
    #     lat: int | None = None,
    #     disable_caller_lookup: bool | None = None,
    #     data_center_provider: str | None = None,
    #     data_center_region: str | None = None,
    #     temporal_granularity: TemporalGranularity | None = None,
    # ) -> PastResponseEnergyShare:
    #     """Get the past carbon free energy for a zone or coordinates."""
    #     return self._api.get_carbon_free_energy_past(
    #         dt=dt,
    #         zone_key=zone_key,
    #         lon=lon,
    #         lat=lat,
    #         disable_caller_lookup=disable_caller_lookup,
    #         data_center_provider=data_center_provider,
    #         data_center_region=data_center_region,
    #         temporal_granularity=temporal_granularity,
    #     )
