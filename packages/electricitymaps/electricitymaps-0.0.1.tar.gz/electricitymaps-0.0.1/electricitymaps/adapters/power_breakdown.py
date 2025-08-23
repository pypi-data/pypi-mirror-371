from openapi.api.power_breakdown_api import PowerBreakdownAPI
from openapi.models.history_response_power_breakdown import (
    HistoryResponsePowerBreakdown,
)
from openapi.models.power_breakdown import PowerBreakdown as PowerBreakdownModel
from openapi.models.temporal_granularity import TemporalGranularity


class PowerBreakdownAdapter:
    """Power breakdown API methods with simplified interface."""

    def __init__(self, api: PowerBreakdownAPI):
        self._api = api

    def latest(
        self,
        temporal_granularity: TemporalGranularity | None = None,
        zone_key: str | None = None,
        lat: int | None = None,
        lon: int | None = None,
        data_center_provider: str | None = None,
        data_center_region: str | None = None,
        disable_caller_lookup: str | None = None,
    ) -> PowerBreakdownModel:
        """Get the latest power breakdown for electricity production/consumption."""
        return self._api.get_power_breakdown_latest(
            temporal_granularity=temporal_granularity,
            zone_key=zone_key,
            lat=lat,
            lon=lon,
            data_center_provider=data_center_provider,
            data_center_region=data_center_region,
            disable_caller_lookup=disable_caller_lookup,
        )

    def history(
        self,
        temporal_granularity: TemporalGranularity | None = None,
        zone_key: str | None = None,
        lat: int | None = None,
        lon: int | None = None,
        data_center_provider: str | None = None,
        data_center_region: str | None = None,
        disable_caller_lookup: str | None = None,
    ) -> HistoryResponsePowerBreakdown:
        """Get the power breakdown history for electricity production/consumption."""
        return self._api.get_power_breakdown_history(
            temporal_granularity=temporal_granularity,
            zone_key=zone_key,
            lat=lat,
            lon=lon,
            data_center_provider=data_center_provider,
            data_center_region=data_center_region,
            disable_caller_lookup=disable_caller_lookup,
        )

    # Currently broken with response
    # def past(
    #     self,
    #     dt: str,
    #     temporal_granularity: TemporalGranularity | None = None,
    #     zone_key: str | None = None,
    #     lat: int | None = None,
    #     lon: int | None = None,
    #     data_center_provider: str | None = None,
    #     data_center_region: str | None = None,
    #     disable_caller_lookup: str | None = None,
    # ) -> PastResponsePowerBreakdown:
    #     """Get the past power breakdown for electricity production/consumption."""
    #     return self._api.get_power_breakdown_past(
    #         dt=dt,
    #         temporal_granularity=temporal_granularity,
    #         zone_key=zone_key,
    #         lat=lat,
    #         lon=lon,
    #         data_center_provider=data_center_provider,
    #         data_center_region=data_center_region,
    #         disable_caller_lookup=disable_caller_lookup,
    #     )
