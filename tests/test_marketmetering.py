# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for the Market Metering client."""

from collections.abc import AsyncIterator
from datetime import datetime, timedelta, timezone
from typing import Any, cast

import pytest

from frequenz.client.marketmetering import MarketMeteringApiClient
from frequenz.client.marketmetering.types import (
    DataQuality,
    DownsamplingMethod,
    EnergyFlowDirection,
    MarketArea,
    MarketLocationId,
    MarketLocationIdType,
    MarketLocationRef,
    MarketLocationSample,
    MarketLocationSeries,
    MetricType,
    MetricUnit,
    ResamplingMethod,
    ResamplingOptions,
    TimeResolution,
)


class TestTypes:
    """Tests for type definitions."""

    def test_market_area_enum(self) -> None:
        """Test MarketArea enum values."""
        assert MarketArea.EU_DE.name == "EU_DE"
        assert MarketArea.EU_UK.name == "EU_UK"
        assert MarketArea.NA_US_ERCOT.name == "NA_US_ERCOT"

    def test_market_location_id_type_enum(self) -> None:
        """Test MarketLocationIdType enum values."""
        assert MarketLocationIdType.MALO_ID.name == "MALO_ID"
        assert MarketLocationIdType.MPAN.name == "MPAN"
        assert MarketLocationIdType.ESI_ID.name == "ESI_ID"

    def test_time_resolution_to_timedelta(self) -> None:
        """Test TimeResolution.to_timedelta."""
        assert TimeResolution.MIN_15.to_timedelta() == timedelta(minutes=15)
        assert TimeResolution.MIN_60.to_timedelta() == timedelta(hours=1)
        assert TimeResolution.DAY_1.to_timedelta() == timedelta(days=1)
        assert TimeResolution.UNSPECIFIED.to_timedelta() is None

    def test_energy_flow_direction_enum(self) -> None:
        """Test EnergyFlowDirection enum values."""
        assert EnergyFlowDirection.IMPORT.name == "IMPORT"
        assert EnergyFlowDirection.EXPORT.name == "EXPORT"

    def test_metric_type_enum(self) -> None:
        """Test MetricType enum values."""
        assert MetricType.ACTIVE_ENERGY.name == "ACTIVE_ENERGY"
        assert MetricType.ACTIVE_POWER.name == "ACTIVE_POWER"

    def test_metric_unit_enum(self) -> None:
        """Test MetricUnit enum values."""
        assert MetricUnit.KWH.name == "KWH"
        assert MetricUnit.KW.name == "KW"
        assert MetricUnit.KVARH.name == "KVARH"

    def test_data_quality_enum(self) -> None:
        """Test DataQuality enum values."""
        assert DataQuality.MEASURED.name == "MEASURED"
        assert DataQuality.ESTIMATED.name == "ESTIMATED"
        assert DataQuality.CORRECTED.name == "CORRECTED"
        assert DataQuality.MISSING.name == "MISSING"

    def test_resampling_method_enum(self) -> None:
        """Test ResamplingMethod enum values."""
        assert ResamplingMethod.NATIVE.name == "NATIVE"
        assert ResamplingMethod.DOWNSAMPLED.name == "DOWNSAMPLED"
        assert ResamplingMethod.UPSAMPLED.name == "UPSAMPLED"


class TestMarketLocationId:
    """Tests for MarketLocationId."""

    def test_create_market_location_id(self) -> None:
        """Test creating a MarketLocationId."""
        ml_id = MarketLocationId(
            value="DE01234567890",
            type=MarketLocationIdType.MALO_ID,
        )
        assert ml_id.value == "DE01234567890"
        assert ml_id.type == MarketLocationIdType.MALO_ID


class TestMarketLocationRef:
    """Tests for MarketLocationRef."""

    def test_create_market_location_ref(self) -> None:
        """Test creating a MarketLocationRef."""
        ml_ref = MarketLocationRef(
            market_area=MarketArea.EU_DE,
            market_location_id=MarketLocationId(
                value="DE01234567890",
                type=MarketLocationIdType.MALO_ID,
            ),
        )
        assert ml_ref.enterprise_id == 0
        assert ml_ref.market_area == MarketArea.EU_DE
        assert ml_ref.market_location_id.value == "DE01234567890"


class TestResamplingOptions:
    """Tests for ResamplingOptions."""

    def test_default_resampling_options(self) -> None:
        """Test default ResamplingOptions."""
        options = ResamplingOptions()
        assert options.resolution is None
        assert options.downsampling_method == DownsamplingMethod.MEAN

    def test_resampling_options_with_resolution(self) -> None:
        """Test ResamplingOptions with resolution."""
        options = ResamplingOptions(resolution=TimeResolution.MIN_15)
        assert options.resolution == TimeResolution.MIN_15


class _UpsertStub:
    """A fake stub capturing upsert stream call arguments."""

    def __init__(self) -> None:
        self.metadata: tuple[tuple[str, str | bytes], ...] | None = None
        self.requests: list[object] = []

    # gRPC-generated method names use UpperCamelCase and this stub mirrors that.
    # pylint: disable=invalid-name,missing-function-docstring
    async def UpsertMarketLocationSamplesStream(  # noqa: N802
        self,
        request_iterator: AsyncIterator[object],
        *,
        metadata: tuple[tuple[str, str | bytes], ...] | None = None,
        timeout: float | None = None,
    ) -> AsyncIterator[object]:
        del timeout
        self.metadata = metadata
        async for request in request_iterator:
            self.requests.append(request)
        items: tuple[object, ...] = ()
        for item in items:
            yield item


class TestClientMethods:
    """Tests for client RPC helpers."""

    @pytest.mark.asyncio
    async def test_upsert_samples_adds_stream_metadata(self) -> None:
        """Test that bidi upsert includes auth and signing metadata."""
        client = MarketMeteringApiClient(
            server_url="grpc://example.com",
            auth_key="test-key",
            sign_secret="test-secret",
            connect=False,
        )
        stub = _UpsertStub()
        setattr(client, "_stub", cast(Any, stub))
        setattr(client, "_channel", cast(Any, object()))

        market_location_ref = MarketLocationRef(
            market_area=MarketArea.EU_DE,
            market_location_id=MarketLocationId(
                value="DE01234567890",
                type=MarketLocationIdType.MALO_ID,
            ),
        )
        series = MarketLocationSeries(
            market_location_ref=market_location_ref,
            direction=EnergyFlowDirection.IMPORT,
            metric_type=MetricType.ACTIVE_ENERGY,
            metric_unit=MetricUnit.KWH,
            resolution=TimeResolution.MIN_15,
            samples=[],
        )
        sample = MarketLocationSample(
            sample_time=datetime.now(timezone.utc),
            value=1.0,
            quality=DataQuality.MEASURED,
            revision=1,
            update_time=None,
            resampling_method=ResamplingMethod.UNSPECIFIED,
        )

        async def sample_generator() -> (
            AsyncIterator[tuple[MarketLocationRef, MarketLocationSeries]]
        ):
            yield (
                market_location_ref,
                MarketLocationSeries(
                    market_location_ref=series.market_location_ref,
                    direction=series.direction,
                    metric_type=series.metric_type,
                    metric_unit=series.metric_unit,
                    resolution=series.resolution,
                    samples=[sample],
                ),
            )

        assert [
            result async for result in client.upsert_samples(sample_generator())
        ] == []
        assert stub.metadata is not None
        metadata = dict(stub.metadata)
        assert metadata["key"] == "test-key"
        assert metadata["ts"]
        assert metadata["nonce"]
        assert metadata["sig"]
        assert len(stub.requests) == 1
