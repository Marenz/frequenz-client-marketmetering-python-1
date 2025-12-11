# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Type definitions for the Market Metering API client."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Self

from frequenz.api.marketmetering.v1alpha1 import marketmetering_pb2 as pb
from google.protobuf.timestamp_pb2 import Timestamp


class MarketArea(Enum):
    """Market area enum representing the jurisdiction."""

    UNSPECIFIED = pb.MARKET_AREA_UNSPECIFIED
    """Unspecified market area."""

    DE = pb.MARKET_AREA_DE
    """Germany (Marktlokation / MaLo)."""

    UK = pb.MARKET_AREA_UK
    """United Kingdom (MPAN)."""

    IT = pb.MARKET_AREA_IT
    """Italy (POD)."""

    AU = pb.MARKET_AREA_AU
    """Australia (NMI)."""

    US_ERCOT = pb.MARKET_AREA_US_ERCOT
    """US - ERCOT region (ESI ID)."""

    OTHER = pb.MARKET_AREA_OTHER
    """Other or not yet modelled areas."""


class MarketLocationIdType(Enum):
    """Type of external market identifier."""

    UNSPECIFIED = pb.OFFICIAL_MARKET_LOCATION_ID_TYPE_UNSPECIFIED
    """Unspecified identifier type."""

    MALO_ID = pb.OFFICIAL_MARKET_LOCATION_ID_TYPE_MALO_ID
    """Germany – Marktlokations-ID (MaLo-ID)."""

    MPAN = pb.OFFICIAL_MARKET_LOCATION_ID_TYPE_MPAN
    """United Kingdom – Meter Point Administration Number."""

    ESI_ID = pb.OFFICIAL_MARKET_LOCATION_ID_TYPE_ESI_ID
    """United States – Electric Service Identifier (ESI ID)."""

    NMI = pb.OFFICIAL_MARKET_LOCATION_ID_TYPE_NMI
    """Australia – National Metering Identifier."""

    OTHER = pb.OFFICIAL_MARKET_LOCATION_ID_TYPE_OTHER
    """Generic meter identifier for markets not modeled explicitly."""


class TimeResolution(Enum):
    """Time resolution for metering data."""

    UNSPECIFIED = pb.TIME_RESOLUTION_UNSPECIFIED
    """Unspecified resolution."""

    MIN_1 = pb.TIME_RESOLUTION_1_MIN
    """1-minute interval."""

    MIN_2 = pb.TIME_RESOLUTION_2_MIN
    """2-minute interval."""

    MIN_5 = pb.TIME_RESOLUTION_5_MIN
    """5-minute interval."""

    MIN_10 = pb.TIME_RESOLUTION_10_MIN
    """10-minute interval."""

    MIN_15 = pb.TIME_RESOLUTION_15_MIN
    """15-minute interval."""

    MIN_30 = pb.TIME_RESOLUTION_30_MIN
    """30-minute interval."""

    MIN_60 = pb.TIME_RESOLUTION_60_MIN
    """60-minute (1 hour) interval."""

    DAY_1 = pb.TIME_RESOLUTION_1_DAY
    """Daily resolution."""

    def to_timedelta(self) -> timedelta | None:
        """Convert to a timedelta.

        Returns:
            The timedelta representation, or None if unspecified.
        """
        mapping = {
            TimeResolution.MIN_1: timedelta(minutes=1),
            TimeResolution.MIN_2: timedelta(minutes=2),
            TimeResolution.MIN_5: timedelta(minutes=5),
            TimeResolution.MIN_10: timedelta(minutes=10),
            TimeResolution.MIN_15: timedelta(minutes=15),
            TimeResolution.MIN_30: timedelta(minutes=30),
            TimeResolution.MIN_60: timedelta(hours=1),
            TimeResolution.DAY_1: timedelta(days=1),
        }
        return mapping.get(self)


class EnergyFlowDirection(Enum):
    """Direction of energy flow for metering samples."""

    UNSPECIFIED = pb.ENERGY_FLOW_DIRECTION_UNSPECIFIED
    """Unspecified direction."""

    IMPORT = pb.ENERGY_FLOW_DIRECTION_IMPORT
    """Energy flowing from grid to customer (consumption)."""

    EXPORT = pb.ENERGY_FLOW_DIRECTION_EXPORT
    """Energy flowing from customer to grid (generation / feed-in)."""


class MetricType(Enum):
    """Fundamental physical property being measured."""

    UNSPECIFIED = pb.METRIC_TYPE_UNSPECIFIED
    """Unspecified metric type."""

    ACTIVE_ENERGY = pb.METRIC_TYPE_ACTIVE_ENERGY
    """Active energy (e.g., kWh, Wh, MWh)."""

    ACTIVE_POWER = pb.METRIC_TYPE_ACTIVE_POWER
    """Active power (e.g., kW, MW)."""

    REACTIVE_ENERGY = pb.METRIC_TYPE_REACTIVE_ENERGY
    """Reactive energy (e.g., kVArh)."""

    REACTIVE_POWER = pb.METRIC_TYPE_REACTIVE_POWER
    """Reactive power (e.g., kVAr, MVAr)."""


class MetricUnit(Enum):
    """Unit of measurement for a sample value."""

    UNSPECIFIED = pb.METRIC_UNIT_UNSPECIFIED
    """Unspecified unit."""

    # Energy units
    WH = pb.METRIC_UNIT_WH
    """Watt-hour (Wh)."""

    KWH = pb.METRIC_UNIT_KWH
    """Kilowatt-hour (kWh)."""

    MWH = pb.METRIC_UNIT_MWH
    """Megawatt-hour (MWh)."""

    # Power units
    W = pb.METRIC_UNIT_W
    """Watt (W)."""

    KW = pb.METRIC_UNIT_KW
    """Kilowatt (kW)."""

    MW = pb.METRIC_UNIT_MW
    """Megawatt (MW)."""

    # Reactive energy units
    VARH = pb.METRIC_UNIT_VARH
    """Volt-ampere-reactive-hour (VArh)."""

    KVARH = pb.METRIC_UNIT_KVARH
    """Kilovolt-ampere-reactive-hour (kVArh)."""

    MVARH = pb.METRIC_UNIT_MVARH
    """Megavolt-ampere-reactive-hour (MVArh)."""

    # Reactive power units
    VAR = pb.METRIC_UNIT_VAR
    """Volt-ampere-reactive (VAr)."""

    KVAR = pb.METRIC_UNIT_KVAR
    """Kilovolt-ampere-reactive (kVAr)."""

    MVAR = pb.METRIC_UNIT_MVAR
    """Megavolt-ampere-reactive (MVAr)."""


class DataQuality(Enum):
    """Classification of data quality for a metering sample."""

    UNSPECIFIED = pb.DATA_QUALITY_UNSPECIFIED
    """Unspecified quality."""

    MEASURED = pb.DATA_QUALITY_MEASURED
    """Raw value directly received from the metering system."""

    ESTIMATED = pb.DATA_QUALITY_ESTIMATED
    """Value inferred or interpolated due to missing or invalid readings."""

    CORRECTED = pb.DATA_QUALITY_CORRECTED
    """Value that was initially delivered but later amended."""

    MISSING = pb.DATA_QUALITY_MISSING
    """No valid value is available for this interval."""


class ResamplingMethod(Enum):
    """Indicates how a returned sample was derived."""

    UNSPECIFIED = pb.RESAMPLING_METHOD_UNSPECIFIED
    """Unspecified method."""

    NATIVE = pb.RESAMPLING_METHOD_NATIVE
    """Sample is stored at this exact resolution."""

    DOWNSAMPLED = pb.RESAMPLING_METHOD_DOWNSAMPLED
    """Sample is computed from finer-granularity data."""

    UPSAMPLED = pb.RESAMPLING_METHOD_UPSAMPLED
    """Sample is computed from coarser-granularity data."""


class DownsamplingMethod(Enum):
    """Defines how multiple native samples are combined when downsampling."""

    UNSPECIFIED = pb.DOWNSAMPLING_METHOD_UNSPECIFIED
    """Defaults to MEAN."""

    MEAN = pb.DOWNSAMPLING_METHOD_MEAN
    """Arithmetic mean of all samples within the interval."""


@dataclass(frozen=True)
class MarketLocationId:
    """Market-standard identifier describing a Market Location.

    A Market Location is a jurisdiction-specific point of metering used for
    regulatory processes such as settlement, billing, supplier switching, etc.
    """

    value: str
    """Opaque identifier in its original market format."""

    type: MarketLocationIdType
    """Type of official market identifier."""

    @classmethod
    def from_protobuf(cls, pb_obj: pb.MarketLocationId) -> Self:
        """Create from protobuf message.

        Args:
            pb_obj: The protobuf message.

        Returns:
            A new MarketLocationId instance.
        """
        return cls(
            value=pb_obj.value,
            type=MarketLocationIdType(pb_obj.type),
        )

    def to_protobuf(self) -> pb.MarketLocationId:
        """Convert to protobuf message.

        Returns:
            The protobuf representation.
        """
        return pb.MarketLocationId(
            value=self.value,
            type=self.type.value,
        )


@dataclass(frozen=True)
class MarketLocationRef:
    """Reference to a Market Location within a specific enterprise."""

    enterprise_id: int
    """Unique enterprise ID for this Market Location."""

    market_location_id: MarketLocationId
    """Market-wide identifier (MaLo, MPAN, ESI-ID, NMI, ...)."""

    @classmethod
    def from_protobuf(cls, pb_obj: pb.MarketLocationRef) -> Self:
        """Create from protobuf message.

        Args:
            pb_obj: The protobuf message.

        Returns:
            A new MarketLocationRef instance.
        """
        return cls(
            enterprise_id=pb_obj.enterprise_id,
            market_location_id=MarketLocationId.from_protobuf(
                pb_obj.market_location_id
            ),
        )

    def to_protobuf(self) -> pb.MarketLocationRef:
        """Convert to protobuf message.

        Returns:
            The protobuf representation.
        """
        return pb.MarketLocationRef(
            enterprise_id=self.enterprise_id,
            market_location_id=self.market_location_id.to_protobuf(),
        )


def _timestamp_to_datetime(ts: Timestamp) -> datetime:
    """Convert a protobuf Timestamp to a datetime.

    Args:
        ts: The protobuf timestamp.

    Returns:
        The datetime representation in UTC.
    """
    return ts.ToDatetime()


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


@dataclass(frozen=True)
class MarketLocationSample:
    """A metering sample with metadata."""

    sample_time: datetime
    """Timestamp of the sample (UTC)."""

    value: float | None
    """Numeric value, if available."""

    quality: DataQuality
    """Quality classification of the sample."""

    revision: int | None
    """Revision number for native samples."""

    update_time: datetime | None
    """Timestamp when the sample was last updated."""

    resampling_method: ResamplingMethod
    """How this sample was produced."""

    @classmethod
    def from_protobuf(cls, pb_obj: pb.MarketLocationSampleDetail) -> Self:
        """Create from protobuf message.

        Args:
            pb_obj: The protobuf message.

        Returns:
            A new MarketLocationSample instance.
        """
        return cls(
            sample_time=_timestamp_to_datetime(pb_obj.sample_time),
            value=pb_obj.value if pb_obj.HasField("value") else None,
            quality=DataQuality(pb_obj.quality),
            revision=pb_obj.revision if pb_obj.HasField("revision") else None,
            update_time=(
                _timestamp_to_datetime(pb_obj.sample_update_time)
                if pb_obj.HasField("sample_update_time")
                else None
            ),
            resampling_method=ResamplingMethod(pb_obj.resampling_method),
        )


@dataclass(frozen=True)
class MarketLocationSeries:
    """A time series for a single logical Market Location."""

    market_location_ref: MarketLocationRef
    """Reference to the Market Location."""

    direction: EnergyFlowDirection
    """Energy-flow direction of this series."""

    metric_type: MetricType
    """Metric type represented by this series."""

    metric_unit: MetricUnit
    """Physical unit in which the metric is expressed."""

    resolution: TimeResolution
    """Market Location's current contractual resolution."""

    samples: list[MarketLocationSample]
    """Ordered samples representing this time series."""

    @classmethod
    def from_protobuf(cls, pb_obj: pb.MarketLocationSeries) -> Self:
        """Create from protobuf message.

        Args:
            pb_obj: The protobuf message.

        Returns:
            A new MarketLocationSeries instance.
        """
        return cls(
            market_location_ref=MarketLocationRef.from_protobuf(
                pb_obj.market_location_ref
            ),
            direction=EnergyFlowDirection(pb_obj.direction),
            metric_type=MetricType(pb_obj.metric_type),
            metric_unit=MetricUnit(pb_obj.metric_unit),
            resolution=TimeResolution(pb_obj.resolution),
            samples=[MarketLocationSample.from_protobuf(s) for s in pb_obj.samples],
        )


@dataclass(frozen=True)
class ResamplingOptions:
    """Resampling options for Market Location time-series data."""

    resolution: TimeResolution | None = None
    """Optional resampling resolution for the output time series."""

    downsampling_method: DownsamplingMethod = DownsamplingMethod.MEAN
    """Aggregation method applied when downsampling."""

    def to_protobuf(self) -> pb.ResamplingOptions:
        """Convert to protobuf message.

        Returns:
            The protobuf representation.
        """
        return pb.ResamplingOptions(
            resolution=self.resolution.value if self.resolution else 0,  # type: ignore[arg-type]
            downsampling_method=self.downsampling_method.value,
        )


__all__ = [
    "DataQuality",
    "DownsamplingMethod",
    "EnergyFlowDirection",
    "MarketArea",
    "MarketLocationId",
    "MarketLocationIdType",
    "MarketLocationRef",
    "MarketLocationSample",
    "MarketLocationSeries",
    "MetricType",
    "MetricUnit",
    "ResamplingMethod",
    "ResamplingOptions",
    "TimeResolution",
]
