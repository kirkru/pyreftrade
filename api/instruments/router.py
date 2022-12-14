from fastapi import Request, Response
from fastapi.routing import APIRoute
from typing import Callable
from .utils import logger, metrics, MetricUnit, single_metric
import warnings

class LoggerRouteHandler(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        # @metrics.log_metrics
        async def route_handler(request: Request) -> Response:
            # Add fastapi context to logs
            ctx = {
                "path": request.url.path,
                "route": self.path,
                "method": request.method,
            }
            logger.append_keys(fastapi=ctx)
            logger.info("Received request")

            warnings.filterwarnings("ignore", "No metrics to publish*")
            # Add count metric for route with route path as dimenision
            with single_metric(
                name="RequestCount", unit=MetricUnit.Count, value=1
            ) as metric:
                metric.add_dimension(
                    name="route", value=f"{request.method} {self.path}"
                )

            return await original_route_handler(request)

        return route_handler