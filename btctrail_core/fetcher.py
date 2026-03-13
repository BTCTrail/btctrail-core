import requests
import json
import logging
from typing import Dict, List, Optional, Any
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataFetcher:
    """
    Handles data ingestion from multiple Bitcoin data sources.
    Prioritizes local Bitcoin Core RPC for privacy, falls back to Electrum/Mempool.
    """
    
    def __init__(self, rpc_url: Optional[str] = None, mempool_api: str = "https://mempool.space/api"):
        self.rpc_url = rpc_url
        self.mempool_api = mempool_api
        self.rpc_conn = None
        
        if rpc_url:
            try:
                self.rpc_conn = AuthServiceProxy(rpc_url)
                # Test connection
                self.rpc_conn.getblockchaininfo()
                logger.info("Successfully connected to Bitcoin Core RPC")
            except Exception as e:
                logger.warning(f"Failed to connect to RPC: {e}. Falling back to Mempool.space API.")
                self.rpc_conn = None

    def get_tx(self, txid: str) -> Optional[Dict[str, Any]]:
        """Fetch transaction details."""
        if self.rpc_conn:
            try:
                # verbosity=2 gives decoded tx with input/output details
                return self.rpc_conn.getrawtransaction(txid, 2)
            except JSONRPCException as e:
                logger.error(f"RPC error fetching tx {txid}: {e}")
        
        # Fallback to Mempool.space
        try:
            response = requests.get(f"{self.mempool_api}/tx/{txid}")
            if response.status_code == 200:
                tx_data = response.json()
                # Normalize format to be somewhat consistent with RPC verbosity=2
                # Note: Mempool.space format differs slightly, but we map essentials
                return {
                    "txid": tx_data["txid"],
                    "vin": tx_data["vin"],
                    "vout": tx_data["vout"],
                    "size": tx_data["size"],
                    "weight": tx_data["weight"],
                    "fee": tx_data["fee"],
                    "status": tx_data["status"]
                }
        except Exception as e:
            logger.error(f"API error fetching tx {txid}: {e}")
            
        return None

    def get_address_utxos(self, address: str) -> List[Dict[str, Any]]:
        """Fetch UTXOs for an address."""
        if self.rpc_conn:
            # Bitcoin Core requires address to be in a wallet or scanned
            # For a general explorer, Electrum/Mempool is often better
            pass
            
        try:
            response = requests.get(f"{self.mempool_api}/address/{address}/utxo")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"API error fetching address UTXOs: {e}")
            
        return []

    def crawl_transaction_tree(self, start_txid: str, depth_limit: int = 3, direction: str = "backwards") -> Dict[str, Any]:
        """
        Recursively crawl transaction inputs or outputs up to a certain depth.
        """
        tree = {}
        
        def _crawl(txid, current_depth):
            if current_depth > depth_limit:
                return None
                
            tx_data = self.get_tx(txid)
            if not tx_data:
                return None
                
            node = {"tx": tx_data, "children": []}
            
            if direction == "backwards":
                for vin in tx_data.get("vin", []):
                    prev_txid = vin.get("txid")
                    if prev_txid:
                        child = _crawl(prev_txid, current_depth + 1)
                        if child:
                            node["children"].append(child)
            else: # forwards
                # Forwards crawling is harder via standard APIs without an index
                # This usually requires scanning address history of all outputs
                pass
                
            return node

        return _crawl(start_txid, 0)
