# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Type definitions for the Market Metering API client."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Iterable, Self

from frequenz.api.common.v1alpha8.pagination import (
    pagination_params_pb2 as pagination_params_pb,
)
from frequenz.api.marketmetering.v1alpha1 import marketmetering_pb2 as pb
from google.protobuf import field_mask_pb2, struct_pb2
from google.protobuf.timestamp_pb2 import Timestamp


class MarketArea(Enum):
    """Market area enum representing the jurisdiction.

    Market areas are organized by geographical region:
    - EU_*: Europe
    - NA_*: North America
    - AP_*: Asia-Pacific
    - OC_*: Oceania
    - EURASIA_*: Eurasia
    """

    UNSPECIFIED = pb.MARKET_AREA_UNSPECIFIED
    """Unspecified market area."""

    # Europe
    EU_DE = pb.MARKET_AREA_EU_DE
    """Germany (Marktlokation / MaLo)."""

    EU_UK = pb.MARKET_AREA_EU_UK
    """United Kingdom (MPAN)."""

    EU_IT = pb.MARKET_AREA_EU_IT
    """Italy (POD)."""

    EU_FR = pb.MARKET_AREA_EU_FR
    """France."""

    EU_ES = pb.MARKET_AREA_EU_ES
    """Spain (CUPS)."""

    EU_NL = pb.MARKET_AREA_EU_NL
    """Netherlands (EAN)."""

    EU_BE = pb.MARKET_AREA_EU_BE
    """Belgium (EAN)."""

    EU_CH = pb.MARKET_AREA_EU_CH
    """Switzerland."""

    EU_AT = pb.MARKET_AREA_EU_AT
    """Austria."""

    EU_NORDICS = pb.MARKET_AREA_EU_NORDICS
    """Nordic countries (Denmark, Finland, Norway, Sweden)."""

    # North America
    NA_US_ERCOT = pb.MARKET_AREA_NA_US_ERCOT
    """US - ERCOT region (ESI ID)."""

    NA_US_PJM = pb.MARKET_AREA_NA_US_PJM
    """US - PJM Interconnection."""

    NA_US_ISONE = pb.MARKET_AREA_NA_US_ISONE
    """US - ISO New England."""

    NA_US_CAISO = pb.MARKET_AREA_NA_US_CAISO
    """US - California ISO."""

    # Asia-Pacific
    AP_JP = pb.MARKET_AREA_AP_JP
    """Japan."""

    AP_CN = pb.MARKET_AREA_AP_CN
    """China."""

    AP_IN = pb.MARKET_AREA_AP_IN
    """India."""

    AP_SG = pb.MARKET_AREA_AP_SG
    """Singapore."""

    # Oceania
    OC_AU = pb.MARKET_AREA_OC_AU
    """Australia (NMI)."""

    OC_NZ = pb.MARKET_AREA_OC_NZ
    """New Zealand (ICP)."""

    # Eurasia
    EURASIA_RU = pb.MARKET_AREA_EURASIA_RU
    """Russia."""

    OTHER = pb.MARKET_AREA_OTHER
    """Other or not yet modelled areas."""


class MarketLocationIdType(Enum):
    """Type of external market identifier."""

    UNSPECIFIED = pb.MARKET_LOCATION_ID_TYPE_UNSPECIFIED
    """Unspecified identifier type."""

    MALO_ID = pb.MARKET_LOCATION_ID_TYPE_MALO_ID
    """Germany – Marktlokations-ID (MaLo-ID)."""

    ZAEHLPUNKT = pb.MARKET_LOCATION_ID_TYPE_ZAEHLPUNKT
    """Austria – Zählpunktbezeichnung."""

    MPAN = pb.MARKET_LOCATION_ID_TYPE_MPAN
    """United Kingdom – Meter Point Administration Number."""

    POD = pb.MARKET_LOCATION_ID_TYPE_POD
    """Italy – Punto di Prelievo (Point of Delivery)."""

    CUPS = pb.MARKET_LOCATION_ID_TYPE_CUPS
    """Spain – Código Unificado de Punto de Suministro."""

    PRM = pb.MARKET_LOCATION_ID_TYPE_PRM
    """France – Point de Référence et Mesure (PRM)."""

    EAN = pb.MARKET_LOCATION_ID_TYPE_EAN
    """European Article Number (used in Netherlands, Belgium, etc.)."""

    GSRN = pb.MARKET_LOCATION_ID_TYPE_GSRN
    """Nordic countries – GS1 Global Service Relation Number."""

    ESI_ID = pb.MARKET_LOCATION_ID_TYPE_ESI_ID
    """United States – Electric Service Identifier (ESI ID)."""

    NMI = pb.MARKET_LOCATION_ID_TYPE_NMI
    """Australia – National Metering Identifier."""

    ICP = pb.MARKET_LOCATION_ID_TYPE_ICP
    """New Zealand – Installation Control Point."""

    SPN = pb.MARKET_LOCATION_ID_TYPE_SPN
    """Japan – Supply Point Number."""

    OTHER = pb.MARKET_LOCATION_ID_TYPE_OTHER
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


class RevisionStrategy(Enum):
    """Strategy for selecting revisions of Market Location data."""

    UNSPECIFIED = pb.REVISION_STRATEGY_UNSPECIFIED
    """Unspecified strategy."""

    LATEST_ONLY = pb.REVISION_STRATEGY_LATEST_ONLY
    """Return only the latest revision of the data."""

    ALL = pb.REVISION_STRATEGY_ALL
    """Return all revisions of the data."""


class MarketLocationChangedField(Enum):
    """Fields that can be tracked for changes in Market Location history."""

    UNSPECIFIED = pb.MARKET_LOCATION_CHANGED_FIELD_UNSPECIFIED
    """Unspecified field."""

    SUPPORTED_DIRECTIONS = pb.MARKET_LOCATION_CHANGED_FIELD_SUPPORTED_DIRECTIONS
    """Supported energy flow directions."""

    TIME_RESOLUTION = pb.MARKET_LOCATION_CHANGED_FIELD_TIME_RESOLUTION
    """Time resolution of the metering data."""

    IS_ACTIVE = pb.MARKET_LOCATION_CHANGED_FIELD_IS_ACTIVE
    """Activity status of the Market Location."""


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


@dataclass(frozen=True)
class PaginationParams:
    """Parameters for pagination."""

    page_size: int | None = None
    """Maximum number of results to return."""

    page_token: str | None = None
    """Token to retrieve the next page of results."""

    def to_protobuf(self) -> pagination_params_pb.PaginationParams:
        """Convert to protobuf message.

        Returns:
            The protobuf representation.
        """
        # Note: We need to check if values are None, because protobuf fields
        # usually default to 0/empty if not set, but explicit checking is safer.
        params = pagination_params_pb.PaginationParams()
        if self.page_size is not None:
            params.page_size = self.page_size
        if self.page_token is not None:
            params.page_token = self.page_token
        return params


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

    def to_protobuf(self) -> int:
        """Convert to protobuf message.

        Returns:
            The protobuf representation (integer enum value).
        """
        return self.value


class SampleUpsertErrorCode(Enum):
    """Error codes for sample upsert operations."""

    UNSPECIFIED = pb.SAMPLE_UPSERT_ERROR_CODE_UNSPECIFIED
    """Unspecified error."""

    REVISION_CONFLICT = pb.SAMPLE_UPSERT_ERROR_CODE_REVISION_CONFLICT
    """The sample revision conflicts with an existing sample."""

    REVISION_TOO_OLD = pb.SAMPLE_UPSERT_ERROR_CODE_REVISION_TOO_OLD
    """The sample revision is older than the current revision."""

    UNSUPPORTED_DIRECTION = pb.SAMPLE_UPSERT_ERROR_CODE_UNSUPPORTED_DIRECTION
    """The direction is not supported by the Market Location."""

    UNSUPPORTED_METRIC_TYPE = pb.SAMPLE_UPSERT_ERROR_CODE_UNSUPPORTED_METRIC_TYPE
    """The metric type is not supported by the Market Location."""

    UNIT_MISMATCH = pb.SAMPLE_UPSERT_ERROR_CODE_UNIT_MISMATCH
    """The metric unit does not match the Market Location's unit."""

    MARKET_LOCATION_NOT_FOUND = pb.SAMPLE_UPSERT_ERROR_CODE_MARKET_LOCATION_NOT_FOUND
    """The Market Location does not exist."""

    MARKET_LOCATION_INACTIVE = pb.SAMPLE_UPSERT_ERROR_CODE_MARKET_LOCATION_INACTIVE
    """The Market Location is inactive."""

    INVALID_TIMESTAMP = pb.SAMPLE_UPSERT_ERROR_CODE_INVALID_TIMESTAMP
    """The sample timestamp is invalid (e.g., misalignment)."""

    STORAGE_FAILURE = pb.SAMPLE_UPSERT_ERROR_CODE_STORAGE_FAILURE
    """Internal storage error."""

    UNKNOWN_ERROR = pb.SAMPLE_UPSERT_ERROR_CODE_UNKNOWN_ERROR
    """Unknown error."""


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


class ActivationFilter(Enum):
    """Filter for Market Location activation status."""

    UNSPECIFIED = pb.ACTIVATION_FILTER_UNSPECIFIED
    """Unspecified filter (defaults to ONLY_ACTIVE)."""

    ONLY_ACTIVE = pb.ACTIVATION_FILTER_ONLY_ACTIVE
    """Return only active Market Locations."""

    ONLY_INACTIVE = pb.ACTIVATION_FILTER_ONLY_INACTIVE
    """Return only inactive Market Locations."""

    ALL = pb.ACTIVATION_FILTER_ALL
    """Return all Market Locations regardless of activation status."""


@dataclass(frozen=True)
class MarketLocation:
    """A Market Location with its configuration."""

    display_name: str
    """Human-readable name of the Market Location."""

    market_area: MarketArea
    """Jurisdiction or market area."""

    supported_directions: list[EnergyFlowDirection]
    """Supported energy flow directions."""

    time_resolution: TimeResolution
    """Time resolution of the metering data."""

    payload: dict[str, Any]
    """Additional arbitrary metadata."""

    @classmethod
    def from_protobuf(cls, pb_obj: pb.MarketLocation) -> Self:
        """Create from protobuf message.

        Args:
            pb_obj: The protobuf message.

        Returns:
            A new MarketLocation instance.
        """
        return cls(
            display_name=pb_obj.display_name,
            market_area=MarketArea(pb_obj.market_area),
            supported_directions=[
                EnergyFlowDirection(d) for d in pb_obj.supported_directions
            ],
            time_resolution=TimeResolution(pb_obj.time_resolution),
            payload=dict(pb_obj.payload.items()),
        )

    def to_protobuf(self) -> pb.MarketLocation:
        """Convert to protobuf message.

        Returns:
            The protobuf representation.
        """
        pb_struct = struct_pb2.Struct()
        pb_struct.update(self.payload)

        return pb.MarketLocation(
            display_name=self.display_name,
            market_area=self.market_area.value,
            supported_directions=[d.value for d in self.supported_directions],
            time_resolution=self.time_resolution.value,
            payload=pb_struct,
        )


@dataclass(frozen=True)
class MarketLocationEntry:
    """A Market Location with its context (Enterprise ID and ref)."""

    enterprise_id: int
    """Enterprise ID owning this Market Location."""

    market_location_ref: MarketLocationRef
    """Reference (enterprise + market-standard ID) for this location."""

    market_location: MarketLocation
    """The Market Location details."""

    @classmethod
    def from_protobuf(
        cls, pb_obj: pb.ListMarketLocationsResponse.MarketLocationEntry
    ) -> Self:
        """Create from protobuf message.

        Args:
            pb_obj: The protobuf message.

        Returns:
            A new MarketLocationEntry instance.
        """
        return cls(
            enterprise_id=pb_obj.enterprise_id,
            market_location_ref=MarketLocationRef.from_protobuf(
                pb_obj.market_location.market_location_ref
            ),
            market_location=MarketLocation.from_protobuf(
                pb_obj.market_location.market_location
            ),
        )


@dataclass(frozen=True)
class MarketLocationUpdate:
    """Fields to update in a Market Location."""

    display_name: str | None = None
    """New display name."""

    supported_directions: list[EnergyFlowDirection] | None = None
    """New supported directions."""

    time_resolution: TimeResolution | None = None
    """New time resolution."""

    payload: dict[str, Any] | None = None
    """New payload (replaces existing payload)."""

    def to_protobuf(
        self,
    ) -> tuple[
        pb.UpdateMarketLocationRequest.MarketLocationUpdate, field_mask_pb2.FieldMask
    ]:
        """Convert to protobuf message and field mask.

        Returns:
            A tuple containing the update message and the field mask.
        """
        update_pb = pb.UpdateMarketLocationRequest.MarketLocationUpdate()
        paths = []

        if self.display_name is not None:
            update_pb.display_name = self.display_name
            paths.append("display_name")

        if self.supported_directions is not None:
            update_pb.supported_directions.extend(
                d.value for d in self.supported_directions
            )
            paths.append("supported_directions")

        if self.time_resolution is not None:
            update_pb.time_resolution = self.time_resolution.value
            paths.append("time_resolution")

        if self.payload is not None:
            pb_struct = struct_pb2.Struct()
            pb_struct.update(self.payload)
            update_pb.payload.CopyFrom(pb_struct)
            paths.append("payload")

        return update_pb, field_mask_pb2.FieldMask(paths=paths)


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
class MarketLocationsFilter:
    """Filter criteria for listing Market Locations."""

    market_location_id_filters: Iterable[MarketLocationId] = field(default_factory=list)
    """Filter by specific Market Location IDs."""

    activation_filter: ActivationFilter = ActivationFilter.ONLY_ACTIVE
    """Filter by activation status (defaults to only active locations)."""

    def to_protobuf(self) -> pb.MarketLocationsFilter:
        """Convert to protobuf message.

        Returns:
            The protobuf representation.
        """
        return pb.MarketLocationsFilter(
            market_location_id_filters=[
                ml_id.to_protobuf() for ml_id in self.market_location_id_filters
            ],
            activation_filter=self.activation_filter.value,
        )


@dataclass(frozen=True)
class RevisionSelection:
    """Selection criteria for revisions of Market Location data."""

    revision_strategy: RevisionStrategy = RevisionStrategy.LATEST_ONLY
    """Strategy for selecting revisions."""

    changed_fields: Iterable[MarketLocationChangedField] = field(default_factory=list)
    """Filter revisions by changed fields (only for REVISION_STRATEGY_ALL)."""

    def to_protobuf(self) -> pb.MarketLocationRevisionSelection:
        """Convert to protobuf message.

        Returns:
            The protobuf representation.
        """
        return pb.MarketLocationRevisionSelection(
            revision_strategy=self.revision_strategy.value,
            changed_fields=[f.value for f in self.changed_fields],
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
    def from_protobuf(
        cls, pb_obj: pb.MarketLocationSample | pb.MarketLocationSampleDetail
    ) -> Self:
        """Create from protobuf message.

        Args:
            pb_obj: The protobuf message (simple or detailed).

        Returns:
            A new MarketLocationSample instance.
        """
        # Handle both MarketLocationSample and MarketLocationSampleDetail
        update_time = None
        if isinstance(pb_obj, pb.MarketLocationSampleDetail) and pb_obj.HasField(
            "sample_update_time"
        ):
            update_time = _timestamp_to_datetime(pb_obj.sample_update_time)

        return cls(
            sample_time=_timestamp_to_datetime(pb_obj.sample_time),
            value=pb_obj.value if pb_obj.HasField("value") else None,
            quality=DataQuality(pb_obj.quality),
            # revision is an int32, which doesn't support HasField in proto3 unless optional.
            # Assuming it's a standard field, 0 is the default.
            # If the API treats 0 as a valid revision, we can just use it.
            # If 0 means "not set", we'd check for 0.
            # Here we assume it's always present or defaults to 0.
            revision=pb_obj.revision,
            update_time=update_time,
            resampling_method=(
                ResamplingMethod(pb_obj.resampling_method)
                if isinstance(pb_obj, pb.MarketLocationSampleDetail)
                # Fallback to UNSPECIFIED if it's a simple MarketLocationSample
                # which does not have this field.
                else ResamplingMethod.UNSPECIFIED
            ),
        )

    def to_protobuf(self) -> pb.MarketLocationSample:
        """Convert to protobuf message.

        Returns:
            The protobuf representation.
        """
        sample = pb.MarketLocationSample(
            sample_time=_datetime_to_timestamp(self.sample_time),
            value=self.value,
            quality=self.quality.value,
        )
        if self.revision is not None:
            sample.revision = self.revision
        return sample


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


@dataclass(frozen=True)
class UpsertResult:
    """Result of a sample upsert operation."""

    market_location_ref: MarketLocationRef
    """Reference to the Market Location."""

    sample: MarketLocationSample
    """The sample that was upserted."""

    success: bool
    """Whether the upsert was successful."""

    error_code: SampleUpsertErrorCode
    """Error code if the upsert failed."""

    error_message: str | None
    """Error message if the upsert failed."""

    @classmethod
    def from_protobuf(
        cls, pb_obj: pb.UpsertMarketLocationSamplesStreamResponse
    ) -> Self:
        """Create from protobuf message.

        Args:
            pb_obj: The protobuf message.

        Returns:
            A new UpsertResult instance.
        """
        return cls(
            market_location_ref=MarketLocationRef.from_protobuf(
                pb_obj.market_location_ref
            ),
            sample=MarketLocationSample.from_protobuf(pb_obj.sample),
            success=pb_obj.success,
            error_code=SampleUpsertErrorCode(pb_obj.error_code),
            error_message=pb_obj.error_message if pb_obj.error_message else None,
        )


__all__ = [
    "ActivationFilter",
    "DataQuality",
    "DownsamplingMethod",
    "EnergyFlowDirection",
    "MarketArea",
    "MarketLocation",
    "MarketLocationChangedField",
    "MarketLocationEntry",
    "MarketLocationId",
    "MarketLocationIdType",
    "MarketLocationRef",
    "MarketLocationSample",
    "MarketLocationSeries",
    "MarketLocationUpdate",
    "MarketLocationsFilter",
    "MetricType",
    "MetricUnit",
    "PaginationParams",
    "ResamplingMethod",
    "ResamplingOptions",
    "RevisionSelection",
    "RevisionStrategy",
    "SampleUpsertErrorCode",
    "TimeResolution",
    "UpsertResult",
]
