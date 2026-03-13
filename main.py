import argparse
import sys
import json
from btctrail_core.fetcher import DataFetcher
from btctrail_core.analyzer import TransactionAnalyzer
from btctrail_core.export import GraphExporter

def main():
    parser = argparse.ArgumentParser(description="btctrail-core: Bitcoin Transaction Graph Analyzer")
    parser.add_argument("txid", help="The transaction ID to start analysis from")
    parser.add_argument("--depth", type=int, default=2, help="Crawling depth limit (default: 2)")
    parser.add_argument("--rpc", help="Bitcoin Core RPC URL (e.g., http://user:pass@localhost:8332)")
    parser.add_argument("--output", default="graph.json", help="Output JSON file name")

    args = parser.parse_args()

    print(f"[*] Initializing btctrail-core engine...")
    fetcher = DataFetcher(rpc_url=args.rpc)
    analyzer = TransactionAnalyzer(fetcher)

    print(f"[*] Crawling graph for TXID: {args.txid} (Depth: {args.depth})...")
    try:
        analyzer.build_graph(args.txid, depth_limit=args.depth)
    except Exception as e:
        print(f"[!] Error building graph: {e}")
        sys.exit(1)

    print(f"[*] Graph built with {len(analyzer.graph.nodes)} nodes and {len(analyzer.graph.edges)} edges.")

    print(f"[*] Exporting to {args.output}...")
    d3_json = GraphExporter.to_d3_json(analyzer.graph)
    GraphExporter.save_to_file(d3_json, args.output)

    print("[+] Analysis complete!")

if __name__ == "__main__":
    main()
