from openapi.api.default_api import DefaultAPI


class OptimizeAdapter:
    """Optimize API methods with simplified interface."""

    def __init__(self, api: DefaultAPI):
        self._api = api

    # Broken because of wrong endpoint in spec file
    # def consumption(
    #     self,
    #     consumption_optimizer_params: ConsumptionOptimizerParams | None = None,
    # ) -> ConsumptionOptimizerResponse:
    #     """Optimize consumption for a given set of locations and optimization metric."""
    #     return self._api.optimize_consumption(
    #         consumption_optimizer_params=consumption_optimizer_params
    #     )
