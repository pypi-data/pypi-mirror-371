from openapi.api.net_load_api import NetLoadAPI
from openapi.models.history_response_load import HistoryResponseLoad
from openapi.models.load import Load
from openapi.models.temporal_granularity import TemporalGranularity


class NetLoadAdapter:
    """Net load API methods with simplified interface."""

    def __init__(self, api: NetLoadAPI):
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
    ) -> Load:
        """Get the latest net load for a zone or coordinates."""
        return self._api.get_net_load_latest(
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
    ) -> HistoryResponseLoad:
        """Get the net load history for a zone or coordinates."""
        return self._api.get_net_load_history(
            temporal_granularity=temporal_granularity,
            zone_key=zone_key,
            lat=lat,
            lon=lon,
            data_center_provider=data_center_provider,
            data_center_region=data_center_region,
            disable_caller_lookup=disable_caller_lookup,
        )

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
    # ) -> PastResponseLoad:
    #     """Get the past net load for a zone or coordinates."""
    #     return self._api.get_net_load_past(
    #         dt=dt,
    #         temporal_granularity=temporal_granularity,
    #         zone_key=zone_key,
    #         lat=lat,
    #         lon=lon,
    #         data_center_provider=data_center_provider,
    #         data_center_region=data_center_region,
    #         disable_caller_lookup=disable_caller_lookup,
    #     )
