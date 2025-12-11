# Frequenz Market Metering Client Release Notes

## Summary

Initial release of the Frequenz Market Metering API client for Python.

## New Features

- `MarketMeteringApiClient`: Main client class for connecting to the Market Metering service
- `stream_samples()`: Async iterator for streaming metering samples from Market Locations
- `stream()`: Channel-based receiver for streaming with automatic reconnection
- CLI tool (`marketmetering-cli`) for quick access to metering data
- Support for multiple market identifier types:
  - MaLo-ID (Germany)
  - MPAN (United Kingdom)
  - ESI-ID (US ERCOT)
  - NMI (Australia)
- Filtering by energy flow direction (IMPORT/EXPORT)
- Multiple metric types (active energy, active power, reactive energy/power)
- Optional resampling for time-series aggregation
