# elib-bitcoincashElectrum

Core modules of a Bitcoin Cash (BCH) Electrum-like library packaged as `elib.bitcoincashElectrum`.

## Features
- Address, transaction, wallet, network, and plugin modules from an Electrum-derived codebase.
- Pure-Python package — suitable for server-side and CLI use.
- No GUI dependencies by default.

## Install (after publishing)
```bash
pip install elib-bch
```

## Usage
```python
from elib.bitcoincashElectrum import Transaction, bitcoin, address, SimpleConfig
print(Transaction, bitcoin, address, SimpleConfig)
```

> Note: Some optional modules may require extra dependencies (e.g., hardware wallet, protobuf, etc.).
