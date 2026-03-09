# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Market Metering API client for Python.

This package provides a Python client for the Frequenz Market Metering API,
which allows streaming historical and real-time metering samples from
Market Locations.

Example:
    ```python
    from datetime import datetime, timezone
    from frequenz.client.marketmetering import MarketMeteringApiClient
    from frequenz.client.marketmetering.types import (
        EnergyFlowDirection,
        MarketArea,
        MarketLocationId,
        MarketLocationIdType,
        MarketLocationRef,
        MetricType,
    )

    client = MarketMeteringApiClient(
        server_url="grpc://marketmetering.example.com",
        auth_key="your-api-key",
        sign_secret="your-sign-secret",
    )

    market_location = MarketLocationRef(
        enterprise_id=42,
        market_area=MarketArea.EU_DE,
        market_location_id=MarketLocationId(
            value="DE01234567890",
            type=MarketLocationIdType.MALO_ID,
        ),
    )

    async for series in client.stream_samples(
        market_locations=[market_location],
        directions=[EnergyFlowDirection.IMPORT],
        metric_types=[MetricType.ACTIVE_ENERGY],
        start_time=datetime(2025, 1, 1, tzinfo=timezone.utc),
    ):
        for sample in series.samples:
            print(f"{sample.sample_time}: {sample.value}")
    ```
"""

from ._client import MarketMeteringApiClient
from .types import (
    ActivationFilter,
    DataQuality,
    DownsamplingMethod,
    EnergyFlowDirection,
    MarketArea,
    MarketLocation,
    MarketLocationChangedField,
    MarketLocationDetail,
    MarketLocationEntry,
    MarketLocationId,
    MarketLocationIdType,
    MarketLocationOperationError,
    MarketLocationOperationErrorCode,
    MarketLocationOperationResult,
    MarketLocationRef,
    MarketLocationSample,
    MarketLocationSeries,
    MarketLocationsFilter,
    MarketLocationUpdate,
    MetricType,
    MetricUnit,
    PaginationParams,
    ResamplingMethod,
    ResamplingOptions,
    RevisionSelection,
    RevisionStrategy,
    SampleUpsertError,
    SampleUpsertErrorCode,
    TimeResolution,
    UpsertResult,
)

__all__ = [
    "ActivationFilter",
    "DataQuality",
    "DownsamplingMethod",
    "EnergyFlowDirection",
    "MarketArea",
    "MarketLocation",
    "MarketLocationChangedField",
    "MarketLocationDetail",
    "MarketLocationEntry",
    "MarketLocationId",
    "MarketLocationIdType",
    "MarketLocationOperationError",
    "MarketLocationOperationErrorCode",
    "MarketLocationOperationResult",
    "MarketLocationRef",
    "MarketLocationSample",
    "MarketLocationSeries",
    "MarketLocationUpdate",
    "MarketLocationsFilter",
    "MarketMeteringApiClient",
    "MetricType",
    "MetricUnit",
    "PaginationParams",
    "ResamplingMethod",
    "ResamplingOptions",
    "RevisionSelection",
    "RevisionStrategy",
    "SampleUpsertError",
    "SampleUpsertErrorCode",
    "TimeResolution",
    "UpsertResult",
]
