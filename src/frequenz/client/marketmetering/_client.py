# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Market Metering API client for Python."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import AsyncIterator, cast

from frequenz.api.common.v1alpha8.types.interval_pb2 import Interval as PBInterval
from frequenz.api.marketmetering.v1alpha1 import marketmetering_pb2 as pb
from frequenz.api.marketmetering.v1alpha1 import marketmetering_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp

from frequenz import channels
from frequenz.client.base.channel import ChannelOptions, SslOptions
from frequenz.client.base.client import BaseApiClient
from frequenz.client.base.exception import ClientNotConnected
from frequenz.client.base.retry import LinearBackoff
from frequenz.client.base.streaming import GrpcStreamBroadcaster

from .types import (
    EnergyFlowDirection,
    MarketLocation,
    MarketLocationEntry,
    MarketLocationRef,
    MarketLocationSeries,
    MarketLocationsFilter,
    MarketLocationUpdate,
    MetricType,
    PaginationParams,
    ResamplingOptions,
    RevisionSelection,
    UpsertResult,
)

DEFAULT_PORT = 443


def _datetime_to_timestamp(dt: datetime) -> Timestamp:
    """Convert a datetime to a protobuf Timestamp.

    Args:
        dt: The datetime to convert.

    Returns:
        The protobuf timestamp representation.
    """
    ts = Timestamp()
    ts.FromDatetime(dt)
    return ts


class MarketMeteringApiClient(
    BaseApiClient[marketmetering_pb2_grpc.MarketMeteringServiceStub]
):
    """Market Metering API client.

    This client provides access to the Market Metering Service, allowing you to
    stream historical and real-time metering samples from Market Locations.

    Example:
        ```python
        from datetime import datetime, timezone
        from frequenz.client.marketmetering import MarketMeteringApiClient
        from frequenz.client.marketmetering.types import (
            EnergyFlowDirection,
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
                print(f"{sample.sample_time}: {sample.value} {series.metric_unit.name}")
        ```
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        *,
        server_url: str,
        auth_key: str,
        sign_secret: str | None = None,
        connect: bool = True,
        call_timeout: timedelta = timedelta(seconds=60),
        stream_timeout: timedelta = timedelta(minutes=5),
    ) -> None:
        """Initialize the client.

        Args:
            server_url: The URL of the server to connect to.
            auth_key: API key to use for authentication.
            sign_secret: Optional secret for signing requests.
            connect: Whether to connect to the service immediately.
            call_timeout: Timeout for gRPC calls, default is 60 seconds.
            stream_timeout: Timeout for gRPC streams, default is 5 minutes.
        """
        super().__init__(
            server_url,
            marketmetering_pb2_grpc.MarketMeteringServiceStub,
            connect=connect,
            channel_defaults=ChannelOptions(
                port=DEFAULT_PORT,
                ssl=SslOptions(enabled=True),
            ),
            auth_key=auth_key,
            sign_secret=sign_secret,
        )

        self._streams: dict[
            tuple[
                tuple[MarketLocationRef, ...],
                tuple[EnergyFlowDirection, ...],
                tuple[MetricType, ...],
            ],
            GrpcStreamBroadcaster[
                pb.ReceiveMarketLocationSamplesStreamResponse, MarketLocationSeries
            ],
        ] = {}

        self._call_timeout_seconds = call_timeout.total_seconds()
        self._stream_timeout_seconds = stream_timeout.total_seconds()

    @property
    def call_timeout(self) -> timedelta:
        """Get the call timeout."""
        return timedelta(seconds=self._call_timeout_seconds)

    @property
    def stream_timeout(self) -> timedelta:
        """Get the stream timeout."""
        return timedelta(seconds=self._stream_timeout_seconds)

    @property
    def stub(self) -> marketmetering_pb2_grpc.MarketMeteringServiceStub:
        """The stub for the service."""
        if self._channel is None or self._stub is None:
            raise ClientNotConnected(server_url=self.server_url, operation="stub")
        return self._stub

    async def create_market_location(
        self,
        *,
        market_location_ref: MarketLocationRef,
        market_location: MarketLocation,
    ) -> None:
        """Create a new Market Location.

        Args:
            market_location_ref: The reference ID for the new location.
            market_location: The configuration of the new location.
        """
        request = pb.CreateMarketLocationRequest(
            market_location_ref=market_location_ref.to_protobuf(),
            market_location=market_location.to_protobuf(),
        )
        await self.stub.CreateMarketLocation(  # type: ignore[misc]
            request,
            timeout=self._call_timeout_seconds,
        )

    async def update_market_location(
        self,
        *,
        market_location_ref: MarketLocationRef,
        update: MarketLocationUpdate,
    ) -> None:
        """Update an existing Market Location.

        Args:
            market_location_ref: The reference ID of the location to update.
            update: The fields to update.
        """
        update_pb, update_mask_pb = update.to_protobuf()
        request = pb.UpdateMarketLocationRequest(
            market_location_ref=market_location_ref.to_protobuf(),
            update_fields=update_pb,
            update_mask=update_mask_pb,
        )
        await self.stub.UpdateMarketLocation(  # type: ignore[misc]
            request,
            timeout=self._call_timeout_seconds,
        )

    async def activate_market_location(
        self,
        *,
        market_location_ref: MarketLocationRef,
    ) -> None:
        """Activate a Market Location.

        Args:
            market_location_ref: The reference ID of the location to activate.
        """
        request = pb.ActivateMarketLocationRequest(
            market_location_refs=[market_location_ref.to_protobuf()],
        )
        await self.stub.ActivateMarketLocation(  # type: ignore[misc]
            request,
            timeout=self._call_timeout_seconds,
        )

    async def deactivate_market_location(
        self,
        *,
        market_location_ref: MarketLocationRef,
    ) -> None:
        """Deactivate a Market Location.

        Args:
            market_location_ref: The reference ID of the location to deactivate.
        """
        request = pb.DeactivateMarketLocationRequest(
            market_location_refs=[market_location_ref.to_protobuf()],
        )
        await self.stub.DeactivateMarketLocation(  # type: ignore[misc]
            request,
            timeout=self._call_timeout_seconds,
        )

    async def list_market_locations(
        self,
        *,
        enterprise_id: int,
        filters: MarketLocationsFilter | None = None,
        revision_selection: RevisionSelection | None = None,
        pagination_params: PaginationParams | None = None,
    ) -> tuple[list[MarketLocationEntry], PaginationParams | None]:
        """List Market Locations.

        Args:
            enterprise_id: Filter by enterprise ID.
            filters: Optional filters for the query.
            revision_selection: Optional revision selection criteria.
            pagination_params: Optional pagination parameters.

        Returns:
            A tuple containing a list of Market Location entries and optional
            pagination parameters for the next page.
        """
        request = pb.ListMarketLocationsRequest(
            enterprise_id=enterprise_id,
            filter=filters.to_protobuf() if filters else None,
            revision_selection=(
                revision_selection.to_protobuf() if revision_selection else None
            ),
            pagination_params=(
                pagination_params.to_protobuf() if pagination_params else None
            ),
        )
        response = await self.stub.ListMarketLocations(  # type: ignore[misc]
            request,
            timeout=self._call_timeout_seconds,
        )

        market_locations = [
            MarketLocationEntry.from_protobuf(ml) for ml in response.market_locations
        ]

        next_page_params = None
        if response.HasField("pagination_info"):
            next_page_params = PaginationParams(
                page_token=response.pagination_info.next_page_token
            )

        return market_locations, next_page_params

    async def upsert_samples(
        self,
        samples_stream: AsyncIterator[tuple[MarketLocationRef, MarketLocationSeries]],
    ) -> AsyncIterator[UpsertResult]:
        """Upsert a stream of metering samples.

        Args:
            samples_stream: An async iterator yielding (MarketLocationRef, MarketLocationSeries)
                tuples. Each series should contain exactly one sample.

        Yields:
            UpsertResult objects indicating success or failure for each sample.
        """

        async def request_generator() -> (
            AsyncIterator[pb.UpsertMarketLocationSamplesStreamRequest]
        ):
            async for ml_ref, series in samples_stream:
                for sample in series.samples:
                    yield pb.UpsertMarketLocationSamplesStreamRequest(
                        market_location_ref=ml_ref.to_protobuf(),
                        direction=series.direction.value,
                        metric_type=series.metric_type.value,
                        metric_unit=series.metric_unit.value,
                        sample=sample.to_protobuf(),
                    )

        response_stream = cast(
            AsyncIterator[pb.UpsertMarketLocationSamplesStreamResponse],
            self.stub.UpsertMarketLocationSamplesStream(
                request_generator(),  # type: ignore[arg-type]
                timeout=self._stream_timeout_seconds,
            ),
        )

        async for response in response_stream:
            yield UpsertResult.from_protobuf(response)

    # pylint: disable=too-many-arguments
    async def stream_samples(
        self,
        *,
        market_locations: list[MarketLocationRef],
        directions: list[EnergyFlowDirection],
        metric_types: list[MetricType],
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        resampling: ResamplingOptions | None = None,
    ) -> AsyncIterator[MarketLocationSeries]:
        """Stream metering samples for Market Locations.

        Streams historical and/or real-time metering samples for one or more
        Market Locations. The stream produces one `MarketLocationSeries` per
        unique combination of Market Location, direction, and metric type.

        Args:
            market_locations: List of Market Location references to stream.
            directions: Energy-flow directions requested (IMPORT and/or EXPORT).
            metric_types: Metric types to request (e.g., ACTIVE_ENERGY, ACTIVE_POWER).
            start_time: Optional start time for historical data.
                If omitted, stream starts from real-time data.
            end_time: Optional end time. If omitted, stream continues in real-time.
            resampling: Optional resampling options for aggregation.

        Yields:
            MarketLocationSeries objects containing samples for each combination
            of Market Location, direction, and metric type.

        Example:
            ```python
            async for series in client.stream_samples(
                market_locations=[market_location],
                directions=[EnergyFlowDirection.IMPORT],
                metric_types=[MetricType.ACTIVE_ENERGY],
            ):
                print(f"Location: {series.market_location_ref.market_location_id.value}")
                for sample in series.samples:
                    print(f"  {sample.sample_time}: {sample.value}")
            ```
        """
        # Build the request
        request = pb.ReceiveMarketLocationSamplesStreamRequest(
            market_location_refs=[ml.to_protobuf() for ml in market_locations],
            directions=[d.value for d in directions],
            metric_types=[mt.value for mt in metric_types],
        )

        # Add stream filter with time interval if specified
        stream_filter = pb.MarketLocationSamplesStreamFilter()

        if start_time or end_time:
            time_filter = pb.TimeFilter()
            interval = PBInterval()
            if start_time:
                interval.start_time.CopyFrom(_datetime_to_timestamp(start_time))
            if end_time:
                interval.end_time.CopyFrom(_datetime_to_timestamp(end_time))
            time_filter.interval.CopyFrom(interval)
            stream_filter.time_filter.CopyFrom(time_filter)

        if resampling:
            stream_filter.resampling_options.CopyFrom(resampling.to_protobuf())

        request.stream_filter.CopyFrom(stream_filter)

        # Make the streaming call
        response_stream = cast(
            AsyncIterator[pb.ReceiveMarketLocationSamplesStreamResponse],
            self.stub.ReceiveMarketLocationSamplesStream(
                request,
                timeout=self._stream_timeout_seconds,
            ),
        )

        async for response in response_stream:
            for series_pb in response.series:
                yield MarketLocationSeries.from_protobuf(series_pb)

    # pylint: disable=too-many-arguments
    def stream(
        self,
        *,
        market_locations: list[MarketLocationRef],
        directions: list[EnergyFlowDirection],
        metric_types: list[MetricType],
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        resampling: ResamplingOptions | None = None,
    ) -> channels.Receiver[MarketLocationSeries]:
        """Get a receiver for streaming metering samples.

        This method returns a channel receiver that can be used to receive
        Market Location sample series. The stream is managed internally and
        supports multiple receivers.

        Args:
            market_locations: List of Market Location references to stream.
            directions: Energy-flow directions requested (IMPORT and/or EXPORT).
            metric_types: Metric types to request (e.g., ACTIVE_ENERGY, ACTIVE_POWER).
            start_time: Optional start time for historical data.
            end_time: Optional end time. If omitted, stream continues in real-time.
            resampling: Optional resampling options for aggregation.

        Returns:
            A channel receiver for MarketLocationSeries objects.

        Example:
            ```python
            receiver = client.stream(
                market_locations=[market_location],
                directions=[EnergyFlowDirection.IMPORT],
                metric_types=[MetricType.ACTIVE_ENERGY],
            )
            async for series in receiver:
                print(f"Received series: {series}")
            ```
        """
        return self._get_stream(
            market_locations=market_locations,
            directions=directions,
            metric_types=metric_types,
            start_time=start_time,
            end_time=end_time,
            resampling=resampling,
        ).new_receiver()

    # pylint: disable=too-many-arguments
    def _get_stream(
        self,
        *,
        market_locations: list[MarketLocationRef],
        directions: list[EnergyFlowDirection],
        metric_types: list[MetricType],
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        resampling: ResamplingOptions | None = None,
    ) -> GrpcStreamBroadcaster[
        pb.ReceiveMarketLocationSamplesStreamResponse, MarketLocationSeries
    ]:
        """Get or create a streaming broadcaster for the given parameters."""
        # Create a key for caching the stream
        key = (
            tuple(market_locations),
            tuple(directions),
            tuple(metric_types),
        )

        broadcaster = self._streams.get(key)
        if broadcaster is not None and not broadcaster.is_running:
            del self._streams[key]
            broadcaster = None

        if broadcaster is None:
            # Build the request
            request = pb.ReceiveMarketLocationSamplesStreamRequest(
                market_location_refs=[ml.to_protobuf() for ml in market_locations],
                directions=[d.value for d in directions],
                metric_types=[mt.value for mt in metric_types],
            )

            # Add stream filter
            stream_filter = pb.MarketLocationSamplesStreamFilter()
            if start_time or end_time:
                time_filter = pb.TimeFilter()
                interval = PBInterval()
                if start_time:
                    interval.start_time.CopyFrom(_datetime_to_timestamp(start_time))
                if end_time:
                    interval.end_time.CopyFrom(_datetime_to_timestamp(end_time))
                time_filter.interval.CopyFrom(interval)
                stream_filter.time_filter.CopyFrom(time_filter)

            if resampling:
                stream_filter.resampling_options.CopyFrom(resampling.to_protobuf())

            request.stream_filter.CopyFrom(stream_filter)

            def transform(
                response: pb.ReceiveMarketLocationSamplesStreamResponse,
            ) -> MarketLocationSeries:
                # Return the first series from the response
                # In practice, responses may have multiple series
                if response.series:
                    return MarketLocationSeries.from_protobuf(response.series[0])
                raise ValueError("Empty response received")

            broadcaster = GrpcStreamBroadcaster(
                stream_name="ReceiveMarketLocationSamplesStream",
                stream_method=lambda: cast(
                    AsyncIterator[pb.ReceiveMarketLocationSamplesStreamResponse],
                    self.stub.ReceiveMarketLocationSamplesStream(
                        request,
                        timeout=self._stream_timeout_seconds,
                    ),
                ),
                transform=transform,
                retry_strategy=LinearBackoff(interval=1, limit=None),
            )
            self._streams[key] = broadcaster

        return broadcaster
