from openapi.api.carbon_intensity_api import CarbonIntensityAPI
from openapi.models.carbon_intensity import (
    CarbonIntensity,
)
from openapi.models.carbon_intensity_forecast_response import (
    CarbonIntensityForecastResponse,
)
from openapi.models.history_response_carbon_intensity import (
    HistoryResponseCarbonIntensity,
)
from openapi.models.temporal_granularity import TemporalGranularity


class CarbonIntensityAdapter:
    """Carbon intensity API methods with simplified interface."""

    def __init__(self, api: CarbonIntensityAPI):
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
    ) -> CarbonIntensity:
        """Get the latest carbon intensity for a zone or coordinates."""
        return self._api.get_carbon_intensity_latest(
            zone_key=zone_key,
            lon=lon,
            lat=lat,
            disable_caller_lookup=disable_caller_lookup,
            data_center_provider=data_center_provider,
            data_center_region=data_center_region,
            temporal_granularity=temporal_granularity,
        )

    def forecast(
        self,
        zone_key: str | None = None,
        lon: int | None = None,
        lat: int | None = None,
        horizon_hours: float | None = None,
        environment: str | None = None,
        disable_caller_lookup: bool | None = None,
        data_center_provider: str | None = None,
        data_center_region: str | None = None,
        temporal_granularity: TemporalGranularity | None = None,
    ) -> CarbonIntensityForecastResponse:
        """Get the carbon intensity forecast for a zone or coordinates."""
        return self._api.get_carbon_intensity_forecast(
            zone_key=zone_key,
            lon=lon,
            lat=lat,
            horizon_hours=horizon_hours,
            environment=environment,
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
    ) -> HistoryResponseCarbonIntensity:
        """Get the carbon intensity history for a zone or coordinates."""
        return self._api.get_carbon_intensity_history(
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
    # ) -> PastResponseCarbonIntensity:
    #     """Get the past carbon intensity for a zone or coordinates."""
    #     return self._api.get_carbon_intensity_past(
    #         dt=dt,
    #         zone_key=zone_key,
    #         lon=lon,
    #         lat=lat,
    #         disable_caller_lookup=disable_caller_lookup,
    #         data_center_provider=data_center_provider,
    #         data_center_region=data_center_region,
    #         temporal_granularity=temporal_granularity,
    #     )
