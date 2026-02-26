# Frequenz Market Metering Client Release Notes

## Summary

Initial release of the Frequenz Market Metering API client for Python.

## New Features

- `MarketMeteringApiClient`: Main client class for connecting to the Market Metering service
- `upsert_samples()`: Bidirectional streaming for upserting metering samples.
- `create_market_location()`: Create a new Market Location. Returns `MarketLocationDetail`.
- `update_market_location()`: Update an existing Market Location. Returns `MarketLocationDetail`.
- `activate_market_locations()`: Activate one or more Market Locations (batch). Returns per-location `MarketLocationOperationResult`.
- `deactivate_market_locations()`: Deactivate one or more Market Locations (batch). Returns per-location `MarketLocationOperationResult`.
- `list_market_locations()`: List Market Locations with filtering and pagination.
- `stream()`: Channel-based receiver for streaming with automatic reconnection
- `MarketLocationDetail`: Server-managed metadata (revision, is_active, create_time, update_time, last_deactivated_time).
- `MarketLocationOperationResult` / `MarketLocationOperationErrorCode`: Per-location results for activate/deactivate operations.
- `UpsertResult.ingest_time`: Server-side timestamp when the sample was ingested.
- `revision_strategy` parameter on `stream_samples()` and `stream()`.
- CLI tool (`marketmetering-cli`) for quick access to metering data
- Support for multiple market identifier types:
  - MaLo-ID (Germany)
  - Zählpunkt (Austria)
  - MPAN (United Kingdom)
  - POD (Italy)
  - CUPS (Spain)
  - PRM (France)
  - EAN (Continental Europe)
  - GSRN (Nordic countries)
  - ESI-ID (United States)
  - NMI (Australia)
  - ICP (New Zealand)
  - SPN (Japan)
- Filtering by energy flow direction (IMPORT/EXPORT)
- Multiple metric types (active energy, active power, reactive energy/power)
- Optional resampling for time-series aggregation

## Improvements

- Add mock tests for all client RPC methods.
- Add integration tests (excluded from CI, run with `uv run pytest -m integration`).

## Breaking Changes

- `activate_market_location()` renamed to `activate_market_locations()` (batch support, returns results).
- `deactivate_market_location()` renamed to `deactivate_market_locations()` (batch support, returns results).
- `create_market_location()` now returns `MarketLocationDetail` instead of `None`.
- `update_market_location()` now returns `MarketLocationDetail` instead of `None`.
- `MarketLocationEntry` now wraps `MarketLocationDetail` via `market_location_detail` field (convenience properties `market_location` and `market_location_ref` preserved).
- `UpsertResult` has a new required field `ingest_time`.

## Bug Fixes

- `update_market_location()`: Add missing `expected_revision` parameter required for optimistic concurrency control.
