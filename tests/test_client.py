# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Mock tests for the MarketMeteringApiClient gRPC methods."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import AsyncIterator
from unittest.mock import AsyncMock, MagicMock

from frequenz.api.common.v1alpha8.pagination import (
    pagination_info_pb2 as pagination_info_pb,
)
from frequenz.api.marketmetering.v1alpha1 import marketmetering_pb2 as pb
from google.protobuf.timestamp_pb2 import Timestamp

from frequenz.client.marketmetering import MarketMeteringApiClient
from frequenz.client.marketmetering.types import (
    ActivationFilter,
    DataQuality,
    EnergyFlowDirection,
    MarketArea,
    MarketLocation,
    MarketLocationId,
    MarketLocationIdType,
    MarketLocationRef,
    MarketLocationSample,
    MarketLocationSeries,
    MarketLocationsFilter,
    MarketLocationUpdate,
    MetricType,
    MetricUnit,
    PaginationParams,
    ResamplingMethod,
    TimeResolution,
)


def _make_client() -> MarketMeteringApiClient:
    """Create a client with a mocked channel."""
    client = MarketMeteringApiClient(
        server_url="grpc://localhost:50051?ssl=false",
        auth_key="test-key",
        connect=False,
    )
    # Inject a mock stub so we don't need a real connection.
    # pylint: disable=protected-access
    client._stub = MagicMock()  # noqa: SLF001
    client._channel = MagicMock()  # noqa: SLF001
    # pylint: enable=protected-access
    return client


def _make_ref(
    enterprise_id: int = 42, malo_id: str = "DE0000000001"
) -> MarketLocationRef:
    return MarketLocationRef(
        enterprise_id=enterprise_id,
        market_area=MarketArea.EU_DE,
        market_location_id=MarketLocationId(
            value=malo_id,
            type=MarketLocationIdType.MALO_ID,
        ),
    )


def _make_location() -> MarketLocation:
    return MarketLocation(
        display_name="Test Location",
        supported_directions=[EnergyFlowDirection.IMPORT],
        time_resolution=TimeResolution.MIN_15,
        payload={},
    )


def _make_timestamp(dt: datetime) -> Timestamp:
    ts = Timestamp()
    ts.FromDatetime(dt)
    return ts


def _make_detail_pb(
    enterprise_id: int = 42,
    malo_id: str = "DE0000000001",
    display_name: str = "Test Location",
    revision: int = 1,
    is_active: bool = True,
) -> pb.MarketLocationDetail:
    """Build a MarketLocationDetail protobuf for mock responses."""
    return pb.MarketLocationDetail(
        market_location_ref=pb.MarketLocationRef(
            enterprise_id=enterprise_id,
            market_area=pb.MARKET_AREA_EU_DE,
            market_location_id=pb.MarketLocationId(
                id=pb.MarketLocationIdValue(value=malo_id),
                type=pb.MARKET_LOCATION_ID_TYPE_MALO_ID,
            ),
        ),
        market_location=pb.MarketLocation(
            display_name=display_name,
            supported_directions=[pb.ENERGY_FLOW_DIRECTION_IMPORT],
            time_resolution=pb.TIME_RESOLUTION_15_MIN,
        ),
        revision=revision,
        is_active=is_active,
        create_time=_make_timestamp(datetime(2025, 1, 1, tzinfo=timezone.utc)),
        update_time=_make_timestamp(datetime(2025, 1, 1, tzinfo=timezone.utc)),
    )


class TestCreateMarketLocation:
    """Tests for create_market_location."""

    async def test_sends_correct_request(self) -> None:
        """Test that create_market_location sends the right protobuf."""
        client = _make_client()
        detail_pb = _make_detail_pb()
        client.stub.CreateMarketLocation = AsyncMock(
            return_value=pb.CreateMarketLocationResponse(market_location=detail_pb)
        )

        ml_ref = _make_ref()
        ml = _make_location()

        result = await client.create_market_location(
            market_location_ref=ml_ref,
            market_location=ml,
        )

        client.stub.CreateMarketLocation.assert_called_once()
        request = client.stub.CreateMarketLocation.call_args[0][0]
        assert isinstance(request, pb.CreateMarketLocationRequest)
        assert request.market_location_ref.enterprise_id == 42
        assert request.market_location_ref.market_location_id.id.value == "DE0000000001"
        assert request.market_location_ref.market_area == pb.MARKET_AREA_EU_DE
        assert request.market_location.display_name == "Test Location"
        assert request.market_location.time_resolution == pb.TIME_RESOLUTION_15_MIN
        assert list(request.market_location.supported_directions) == [
            pb.ENERGY_FLOW_DIRECTION_IMPORT
        ]
        assert result.revision == 1
        assert result.is_active is True

    async def test_with_payload(self) -> None:
        """Test that payload is correctly serialized."""
        client = _make_client()
        detail_pb = _make_detail_pb(display_name="With Payload")
        client.stub.CreateMarketLocation = AsyncMock(
            return_value=pb.CreateMarketLocationResponse(market_location=detail_pb)
        )

        ml_ref = _make_ref()
        ml = MarketLocation(
            display_name="With Payload",
            supported_directions=[EnergyFlowDirection.IMPORT],
            time_resolution=TimeResolution.MIN_15,
            payload={"key": "value", "num": 42},
        )

        await client.create_market_location(
            market_location_ref=ml_ref,
            market_location=ml,
        )

        request = client.stub.CreateMarketLocation.call_args[0][0]
        assert request.market_location.payload["key"] == "value"
        assert request.market_location.payload["num"] == 42


class TestUpdateMarketLocation:
    """Tests for update_market_location."""

    async def test_sends_expected_revision(self) -> None:
        """Test that expected_revision is passed through."""
        client = _make_client()
        detail_pb = _make_detail_pb(revision=4)
        client.stub.UpdateMarketLocation = AsyncMock(
            return_value=pb.UpdateMarketLocationResponse(
                market_location_detail=detail_pb
            )
        )

        ml_ref = _make_ref()
        update = MarketLocationUpdate(display_name="New Name")

        result = await client.update_market_location(
            market_location_ref=ml_ref,
            update=update,
            expected_revision=3,
        )

        request = client.stub.UpdateMarketLocation.call_args[0][0]
        assert isinstance(request, pb.UpdateMarketLocationRequest)
        assert request.expected_revision == 3
        assert result.revision == 4

    async def test_update_display_name(self) -> None:
        """Test updating display_name sets the correct field mask."""
        client = _make_client()
        detail_pb = _make_detail_pb()
        client.stub.UpdateMarketLocation = AsyncMock(
            return_value=pb.UpdateMarketLocationResponse(
                market_location_detail=detail_pb
            )
        )

        update = MarketLocationUpdate(display_name="Updated")

        await client.update_market_location(
            market_location_ref=_make_ref(),
            update=update,
            expected_revision=1,
        )

        request = client.stub.UpdateMarketLocation.call_args[0][0]
        assert "display_name" in request.update_mask.paths
        assert request.update_fields.display_name == "Updated"

    async def test_update_supported_directions(self) -> None:
        """Test updating supported_directions."""
        client = _make_client()
        detail_pb = _make_detail_pb()
        client.stub.UpdateMarketLocation = AsyncMock(
            return_value=pb.UpdateMarketLocationResponse(
                market_location_detail=detail_pb
            )
        )

        update = MarketLocationUpdate(
            supported_directions=[
                EnergyFlowDirection.IMPORT,
                EnergyFlowDirection.EXPORT,
            ]
        )

        await client.update_market_location(
            market_location_ref=_make_ref(),
            update=update,
            expected_revision=1,
        )

        request = client.stub.UpdateMarketLocation.call_args[0][0]
        assert "supported_directions" in request.update_mask.paths
        assert list(request.update_fields.supported_directions) == [
            pb.ENERGY_FLOW_DIRECTION_IMPORT,
            pb.ENERGY_FLOW_DIRECTION_EXPORT,
        ]

    async def test_update_time_resolution(self) -> None:
        """Test updating time_resolution."""
        client = _make_client()
        detail_pb = _make_detail_pb()
        client.stub.UpdateMarketLocation = AsyncMock(
            return_value=pb.UpdateMarketLocationResponse(
                market_location_detail=detail_pb
            )
        )

        update = MarketLocationUpdate(time_resolution=TimeResolution.MIN_5)

        await client.update_market_location(
            market_location_ref=_make_ref(),
            update=update,
            expected_revision=1,
        )

        request = client.stub.UpdateMarketLocation.call_args[0][0]
        assert "time_resolution" in request.update_mask.paths
        assert request.update_fields.time_resolution == pb.TIME_RESOLUTION_5_MIN

    async def test_update_payload(self) -> None:
        """Test updating payload."""
        client = _make_client()
        detail_pb = _make_detail_pb()
        client.stub.UpdateMarketLocation = AsyncMock(
            return_value=pb.UpdateMarketLocationResponse(
                market_location_detail=detail_pb
            )
        )

        update = MarketLocationUpdate(payload={"new_key": "new_value"})

        await client.update_market_location(
            market_location_ref=_make_ref(),
            update=update,
            expected_revision=1,
        )

        request = client.stub.UpdateMarketLocation.call_args[0][0]
        assert "payload" in request.update_mask.paths
        assert request.update_fields.payload["new_key"] == "new_value"

    async def test_update_multiple_fields(self) -> None:
        """Test updating multiple fields at once."""
        client = _make_client()
        detail_pb = _make_detail_pb(revision=6)
        client.stub.UpdateMarketLocation = AsyncMock(
            return_value=pb.UpdateMarketLocationResponse(
                market_location_detail=detail_pb
            )
        )

        update = MarketLocationUpdate(
            display_name="Multi",
            time_resolution=TimeResolution.MIN_1,
            payload={"a": 1},
        )

        await client.update_market_location(
            market_location_ref=_make_ref(),
            update=update,
            expected_revision=5,
        )

        request = client.stub.UpdateMarketLocation.call_args[0][0]
        assert set(request.update_mask.paths) == {
            "display_name",
            "time_resolution",
            "payload",
        }
        assert request.expected_revision == 5


class TestListMarketLocations:
    """Tests for list_market_locations."""

    async def test_basic_list(self) -> None:
        """Test listing market locations returns parsed entries."""
        client = _make_client()

        # Build a mock response with one entry.
        ml_pb = pb.MarketLocation(
            display_name="Listed",
            supported_directions=[pb.ENERGY_FLOW_DIRECTION_IMPORT],
            time_resolution=pb.TIME_RESOLUTION_15_MIN,
        )
        ref_pb = pb.MarketLocationRef(
            enterprise_id=42,
            market_area=pb.MARKET_AREA_EU_DE,
            market_location_id=pb.MarketLocationId(
                id=pb.MarketLocationIdValue(value="DE0000000001"),
                type=pb.MARKET_LOCATION_ID_TYPE_MALO_ID,
            ),
        )
        detail_pb = pb.MarketLocationDetail(
            market_location_ref=ref_pb,
            market_location=ml_pb,
            revision=1,
            is_active=True,
            create_time=_make_timestamp(datetime(2025, 1, 1, tzinfo=timezone.utc)),
            update_time=_make_timestamp(datetime(2025, 1, 1, tzinfo=timezone.utc)),
        )
        entry_pb = pb.ListMarketLocationsResponse.MarketLocationEntry(
            enterprise_id=42,
            market_location=detail_pb,
        )
        response = pb.ListMarketLocationsResponse(market_locations=[entry_pb])

        client.stub.ListMarketLocations = AsyncMock(return_value=response)

        entries, next_page = await client.list_market_locations(enterprise_id=42)

        assert len(entries) == 1
        assert entries[0].enterprise_id == 42
        assert entries[0].market_location.display_name == "Listed"
        assert entries[0].market_location_ref.market_area == MarketArea.EU_DE
        assert next_page is None

    async def test_sends_enterprise_id(self) -> None:
        """Test that enterprise_id is sent in the request."""
        client = _make_client()
        response = pb.ListMarketLocationsResponse()
        client.stub.ListMarketLocations = AsyncMock(return_value=response)

        await client.list_market_locations(enterprise_id=99)

        request = client.stub.ListMarketLocations.call_args[0][0]
        assert request.enterprise_id == 99

    async def test_pagination(self) -> None:
        """Test that pagination info is returned."""
        client = _make_client()

        pagination_info = pagination_info_pb.PaginationInfo(next_page_token="token123")
        response = pb.ListMarketLocationsResponse(pagination_info=pagination_info)
        client.stub.ListMarketLocations = AsyncMock(return_value=response)

        _, next_page = await client.list_market_locations(enterprise_id=1)

        assert next_page is not None
        assert next_page.page_token == "token123"

    async def test_sends_filters(self) -> None:
        """Test that filters are sent in the request."""
        client = _make_client()
        response = pb.ListMarketLocationsResponse()
        client.stub.ListMarketLocations = AsyncMock(return_value=response)

        filters = MarketLocationsFilter(
            market_location_id_filters=[
                MarketLocationId(value="DE123", type=MarketLocationIdType.MALO_ID)
            ],
            activation_filter=ActivationFilter.ALL,
        )
        await client.list_market_locations(enterprise_id=1, filters=filters)

        request = client.stub.ListMarketLocations.call_args[0][0]
        assert request.filter.activation_filter == pb.ACTIVATION_FILTER_ALL
        assert len(request.filter.market_location_id_filters) == 1
        assert request.filter.market_location_id_filters[0].value == "DE123"

    async def test_sends_page_size(self) -> None:
        """Test that page_size is sent in the request.

        page_size and page_token are in a oneof, so only one can be set.
        """
        client = _make_client()
        response = pb.ListMarketLocationsResponse()
        client.stub.ListMarketLocations = AsyncMock(return_value=response)

        params = PaginationParams(page_size=10)
        await client.list_market_locations(enterprise_id=1, pagination_params=params)

        request = client.stub.ListMarketLocations.call_args[0][0]
        assert request.pagination_params.page_size == 10

    async def test_sends_page_token(self) -> None:
        """Test that page_token is sent in the request.

        page_size and page_token are in a oneof, so only one can be set.
        """
        client = _make_client()
        response = pb.ListMarketLocationsResponse()
        client.stub.ListMarketLocations = AsyncMock(return_value=response)

        params = PaginationParams(page_token="next-page-token")
        await client.list_market_locations(enterprise_id=1, pagination_params=params)

        request = client.stub.ListMarketLocations.call_args[0][0]
        assert request.pagination_params.page_token == "next-page-token"


class TestActivateMarketLocations:
    """Tests for activate_market_locations."""

    async def test_sends_correct_request(self) -> None:
        """Test that activate sends the refs in market_location_refs."""
        client = _make_client()

        ml_ref_pb = pb.MarketLocationRef(
            enterprise_id=7,
            market_area=pb.MARKET_AREA_EU_DE,
            market_location_id=pb.MarketLocationId(
                id=pb.MarketLocationIdValue(value="DE_ACT_001"),
                type=pb.MARKET_LOCATION_ID_TYPE_MALO_ID,
            ),
        )
        result_pb = pb.MarketLocationOperationResult(
            market_location_ref=ml_ref_pb,
            revision=2,
        )
        client.stub.ActivateMarketLocation = AsyncMock(
            return_value=pb.ActivateMarketLocationResponse(results=[result_pb])
        )

        ml_ref = _make_ref(enterprise_id=7, malo_id="DE_ACT_001")

        results = await client.activate_market_locations(market_location_refs=[ml_ref])

        request = client.stub.ActivateMarketLocation.call_args[0][0]
        assert isinstance(request, pb.ActivateMarketLocationRequest)
        assert len(request.market_location_refs) == 1
        assert request.market_location_refs[0].enterprise_id == 7
        assert (
            request.market_location_refs[0].market_location_id.id.value == "DE_ACT_001"
        )
        assert len(results) == 1
        assert results[0].error is None
        assert results[0].revision == 2


class TestDeactivateMarketLocations:
    """Tests for deactivate_market_locations."""

    async def test_sends_correct_request(self) -> None:
        """Test that deactivate sends the refs in market_location_refs."""
        client = _make_client()

        ml_ref_pb = pb.MarketLocationRef(
            enterprise_id=8,
            market_area=pb.MARKET_AREA_EU_DE,
            market_location_id=pb.MarketLocationId(
                id=pb.MarketLocationIdValue(value="DE_DEACT_001"),
                type=pb.MARKET_LOCATION_ID_TYPE_MALO_ID,
            ),
        )
        result_pb = pb.MarketLocationOperationResult(
            market_location_ref=ml_ref_pb,
            revision=3,
        )
        client.stub.DeactivateMarketLocation = AsyncMock(
            return_value=pb.DeactivateMarketLocationResponse(results=[result_pb])
        )

        ml_ref = _make_ref(enterprise_id=8, malo_id="DE_DEACT_001")

        results = await client.deactivate_market_locations(
            market_location_refs=[ml_ref]
        )

        request = client.stub.DeactivateMarketLocation.call_args[0][0]
        assert isinstance(request, pb.DeactivateMarketLocationRequest)
        assert len(request.market_location_refs) == 1
        assert request.market_location_refs[0].enterprise_id == 8
        assert len(results) == 1
        assert results[0].error is None


class TestStreamSamples:
    """Tests for stream_samples."""

    async def test_yields_parsed_series(self) -> None:
        """Test that stream_samples yields MarketLocationSeries."""
        client = _make_client()

        ml_ref_pb = pb.MarketLocationRef(
            enterprise_id=42,
            market_area=pb.MARKET_AREA_EU_DE,
            market_location_id=pb.MarketLocationId(
                id=pb.MarketLocationIdValue(value="DE001"),
                type=pb.MARKET_LOCATION_ID_TYPE_MALO_ID,
            ),
        )
        sample_time = _make_timestamp(datetime(2025, 1, 1, tzinfo=timezone.utc))
        sample_pb = pb.MarketLocationSampleDetail(
            sample_time=sample_time,
            value=100.5,
            quality=pb.DATA_QUALITY_MEASURED,
            revision=1,
            resampling_method=pb.RESAMPLING_METHOD_NATIVE,
        )
        series_pb = pb.MarketLocationSeries(
            market_location_ref=ml_ref_pb,
            direction=pb.ENERGY_FLOW_DIRECTION_IMPORT,
            metric_type=pb.METRIC_TYPE_ACTIVE_ENERGY,
            metric_unit=pb.METRIC_UNIT_KWH,
            resolution=pb.TIME_RESOLUTION_15_MIN,
            samples=[sample_pb],
        )
        response = pb.ReceiveMarketLocationSamplesStreamResponse(series=[series_pb])

        # Mock the streaming call to return an async iterator.
        async def mock_stream() -> (
            AsyncIterator[pb.ReceiveMarketLocationSamplesStreamResponse]
        ):
            yield response

        client.stub.ReceiveMarketLocationSamplesStream = MagicMock(
            return_value=mock_stream()
        )

        results: list[MarketLocationSeries] = []
        async for series in client.stream_samples(
            market_locations=[_make_ref()],
            directions=[EnergyFlowDirection.IMPORT],
            metric_types=[MetricType.ACTIVE_ENERGY],
        ):
            results.append(series)

        assert len(results) == 1
        assert results[0].direction == EnergyFlowDirection.IMPORT
        assert results[0].metric_type == MetricType.ACTIVE_ENERGY
        assert results[0].metric_unit == MetricUnit.KWH
        assert len(results[0].samples) == 1
        assert results[0].samples[0].value == 100.5

    async def test_sends_time_filter(self) -> None:
        """Test that start_time and end_time are sent."""
        client = _make_client()

        async def mock_stream() -> (
            AsyncIterator[pb.ReceiveMarketLocationSamplesStreamResponse]
        ):
            return
            yield  # make it an async generator  # noqa: RET504

        client.stub.ReceiveMarketLocationSamplesStream = MagicMock(
            return_value=mock_stream()
        )

        start = datetime(2025, 1, 1, tzinfo=timezone.utc)
        end = datetime(2025, 1, 2, tzinfo=timezone.utc)

        async for _ in client.stream_samples(
            market_locations=[_make_ref()],
            directions=[EnergyFlowDirection.IMPORT],
            metric_types=[MetricType.ACTIVE_ENERGY],
            start_time=start,
            end_time=end,
        ):
            pass

        request = client.stub.ReceiveMarketLocationSamplesStream.call_args[0][0]
        assert request.stream_filter.HasField("time_filter")
        interval = request.stream_filter.time_filter.interval
        assert interval.start_time == _make_timestamp(start)
        assert interval.end_time == _make_timestamp(end)


class TestUpsertSamples:
    """Tests for upsert_samples."""

    async def test_yields_parsed_results(self) -> None:
        """Test that upsert_samples yields UpsertResult."""
        client = _make_client()

        ml_ref_pb = pb.MarketLocationRef(
            enterprise_id=42,
            market_area=pb.MARKET_AREA_EU_DE,
            market_location_id=pb.MarketLocationId(
                id=pb.MarketLocationIdValue(value="DE001"),
                type=pb.MARKET_LOCATION_ID_TYPE_MALO_ID,
            ),
        )
        sample_time = _make_timestamp(datetime(2025, 1, 1, tzinfo=timezone.utc))
        sample_pb = pb.MarketLocationSample(
            sample_time=sample_time,
            value=50.0,
            quality=pb.DATA_QUALITY_MEASURED,
            revision=1,
        )
        upsert_response = pb.UpsertMarketLocationSamplesStreamResponse(
            market_location_ref=ml_ref_pb,
            direction=pb.ENERGY_FLOW_DIRECTION_IMPORT,
            metric_type=pb.METRIC_TYPE_ACTIVE_ENERGY,
            metric_unit=pb.METRIC_UNIT_KWH,
            sample=sample_pb,
        )

        async def mock_stream() -> (
            AsyncIterator[pb.UpsertMarketLocationSamplesStreamResponse]
        ):
            yield upsert_response

        client.stub.UpsertMarketLocationSamplesStream = MagicMock(
            return_value=mock_stream()
        )

        # Build an input stream.
        ml_ref = _make_ref()
        sample = MarketLocationSample(
            sample_time=datetime(2025, 1, 1, tzinfo=timezone.utc),
            value=50.0,
            quality=DataQuality.MEASURED,
            revision=1,
            update_time=None,
            resampling_method=ResamplingMethod.UNSPECIFIED,
        )
        series = MarketLocationSeries(
            market_location_ref=ml_ref,
            direction=EnergyFlowDirection.IMPORT,
            metric_type=MetricType.ACTIVE_ENERGY,
            metric_unit=MetricUnit.KWH,
            resolution=TimeResolution.MIN_15,
            samples=[sample],
        )

        async def input_stream() -> (
            AsyncIterator[tuple[MarketLocationRef, MarketLocationSeries]]
        ):
            yield (ml_ref, series)

        results = []
        async for result in client.upsert_samples(input_stream()):
            results.append(result)

        assert len(results) == 1
        assert results[0].error is None
        assert results[0].sample.value == 50.0
