# btctrail-core

The foundational Python engine for Bitcoin transaction graph analysis and privacy auditing.

## Features
- **Data Agnostic**: Fetch data from local Bitcoin Core RPC or public APIs (Mempool.space).
- **Privacy Heuristics**: Automatic detection of Common Input Ownership (CIOH) and Change Addresses.
- **Graph Modeling**: Uses `networkx` for representng the complex flow of UTXOs.
- **Frontend Ready**: Exports directly to D3.js compatible JSON.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run a Sample Analysis
Replace `<TXID>` with a real Bitcoin transaction ID.
```bash
python main.py <TXID> --depth 2
```

### 3. Visualize
The engine will generate `graph.json`. This file can be dropped into any D3.js or React Flow visualization component.

## Architecture
- `fetcher.py`: Handles multi-source data ingestion.
- `heuristics.py`: Core logic for identifying privacy leaks.
- `analyzer.py`: Orchestrates graph building and taint mapping.
- `export.py`: Serializes results for the web.

## Settings
You can set your local Bitcoin Core credentials via CLI:
```bash
python main.py <TXID> --rpc http://user:pass@localhost:8332
```
