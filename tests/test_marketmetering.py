# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for the Market Metering client."""

from datetime import timedelta

from frequenz.client.marketmetering.types import (
    DataQuality,
    DownsamplingMethod,
    EnergyFlowDirection,
    MarketArea,
    MarketLocationId,
    MarketLocationIdType,
    MarketLocationRef,
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
            enterprise_id=42,
            market_location_id=MarketLocationId(
                value="DE01234567890",
                type=MarketLocationIdType.MALO_ID,
            ),
        )
        assert ml_ref.enterprise_id == 42
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
