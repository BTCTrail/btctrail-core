import networkx as nx
from typing import Dict, List, Any, Optional
from .fetcher import DataFetcher
from .heuristics import HeuristicsEngine

class TransactionAnalyzer:
    """
    Builds a transaction graph and calculates taint scores.
    """

    def __init__(self, fetcher: DataFetcher):
        self.fetcher = fetcher
        self.graph = nx.DiGraph()
        self.heuristics = HeuristicsEngine()

    def build_graph(self, target_txid: str, depth_limit: int = 3):
        """
        Builds a DiGraph of the transaction history.
        """
        processed_txs = set()
        
        def _add_to_graph(txid, current_depth):
            if current_depth >= depth_limit or txid in processed_txs:
                return
            
            tx_data = self.fetcher.get_tx(txid)
            if not tx_data:
                return

            processed_txs.add(txid)
            
            # Add transaction node
            self.graph.add_node(txid, type="transaction", label=f"TX: {txid[:8]}...", data=tx_data)
            
            # Analyze privacy
            change_addr = self.heuristics.identify_change(tx_data)
            input_cluster = self.heuristics.check_cioh(tx_data)

            # Process Inputs
            for vin in tx_data.get("vin", []):
                prev_txid = vin.get("txid")
                # Mempool.space vs RPC addressing
                addr = vin.get("prevout", {}).get("scriptpubkey_address") or vin.get("address")
                val = vin.get("prevout", {}).get("value") or vin.get("value", 0)

                if addr:
                    self.graph.add_node(addr, type="address", label=addr[:8]...)
                    self.graph.add_edge(addr, txid, value=val)
                
                if prev_txid:
                    self.graph.add_edge(prev_txid, txid, type="input_flow")
                    _add_to_graph(prev_txid, current_depth + 1)

            # Process Outputs
            for vout in tx_data.get("vout", []):
                addr = vout.get("scriptpubkey_address") or vout.get("scriptPubKey", {}).get("address")
                val = vout.get("value", 0)
                
                if addr:
                    is_change = (addr == change_addr)
                    self.graph.add_node(addr, type="address", label=addr[:8]..., is_change=is_change)
                    self.graph.add_edge(txid, addr, value=val, is_change=is_change)

        _add_to_graph(target_txid, 0)

    def calculate_taint(self, target_address: str, source_txid_or_addr: str) -> float:
        """
        Calculates the percentage of funds in target_address that originated from source.
        This is a simplified 'FIFO' or 'Proportional' taint model.
        """
        # In a real implementation, we would traverse the DAG from source to target
        # and multiply the ratios of flow at each hop.
        # For this foundational version, we'll return a placeholder or simple logic.
        return 1.0 # Placeholder for full implementation
