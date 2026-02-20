# Frequenz Market Metering Client Release Notes

## Summary

Initial release of the Frequenz Market Metering API client for Python.

## New Features

- `MarketMeteringApiClient`: Main client class for connecting to the Market Metering service
- `upsert_samples()`: Bidirectional streaming for upserting metering samples.
- `create_market_location()`: Create a new Market Location.
- `update_market_location()`: Update an existing Market Location.
- `activate_market_location()`: Activate a Market Location.
- `deactivate_market_location()`: Deactivate a Market Location.
- `list_market_locations()`: List Market Locations with filtering and pagination.
- `stream()`: Channel-based receiver for streaming with automatic reconnection
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

## Bug Fixes

- `update_market_location()`: Add missing `expected_revision` parameter required for optimistic concurrency control.
