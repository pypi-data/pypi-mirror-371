from openapi.api.default_api import DefaultAPI


class DefaultAdapter:
    """Default API methods with simplified interface."""

    def __init__(self, api: DefaultAPI):
        self._api = api

    # Broken because of type error
    # def zones(self) -> ZonesResponse:
    #     """Get the zones available."""
    #     return self._api.get_zones()
