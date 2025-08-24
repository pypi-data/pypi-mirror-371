# Platform Observability Python SDK

A Python SDK for ingesting logs and interacting with the Platform Observability service by Red Duck Labs.

## Installation

This package can be installed from PyPI (after publishing):

```
pip install platform-observability-sdk
```

## Quick start

```python
from platform_observability import ObservabilityClient, LogEntry, LogLevel

client = ObservabilityClient(api_key="YOUR_API_KEY")
client.ingest_logs([
    LogEntry(message="Hello from SDK", level=LogLevel.INFO).to_dict()
])
```

## CLI

After installation, a small helper CLI `obs-cli` is available:

```
obs-cli --help
```

## Development

- Python >= 3.8
- Build wheel:

```
pip install build
python -m build
```

- Run tests:

```
pip install .[dev]
pytest
```
