from openapi.api.price_day_ahead_api import PriceDayAheadAPI
from openapi.models.history_response_price_day_ahead import HistoryResponsePriceDayAhead
from openapi.models.price_day_ahead import PriceDayAhead
from openapi.models.temporal_granularity import TemporalGranularity


class PriceDayAheadAdapter:
    """Price day ahead API methods with simplified interface."""

    def __init__(self, api: PriceDayAheadAPI):
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
    ) -> PriceDayAhead:
        """Get the latest price day ahead for a zone or coordinates."""
        return self._api.get_price_day_ahead_latest(
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
    ) -> HistoryResponsePriceDayAhead:
        """Get the price day ahead history for a zone or coordinates."""
        return self._api.get_price_day_ahead_history(
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
    # ) -> PastResponsePriceDayAhead:
    #     """Get the past price day ahead for a zone or coordinates."""
    #     return self._api.get_price_day_ahead_past(
    #         dt=dt,
    #         temporal_granularity=temporal_granularity,
    #         zone_key=zone_key,
    #         lat=lat,
    #         lon=lon,
    #         data_center_provider=data_center_provider,
    #         data_center_region=data_center_region,
    #         disable_caller_lookup=disable_caller_lookup,
    #     )
