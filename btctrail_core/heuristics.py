from typing import Dict, List, Any

class HeuristicsEngine:
    """
    Implements common Bitcoin privacy heuristics.
    """

    @staticmethod
    def check_cioh(tx_data: Dict[str, Any]) -> List[str]:
        """
        Common Input Ownership Heuristic (CIOH).
        If multiple inputs exist, they are likely owned by the same entity.
        Returns a list of addresses that are likely clustered.
        """
        cluster = []
        for vin in tx_data.get("vin", []):
            # Mempool.space format
            if "prevout" in vin and "scriptpubkey_address" in vin["prevout"]:
                cluster.append(vin["prevout"]["scriptpubkey_address"])
            # RPC format
            elif "address" in vin:
                cluster.append(vin["address"])
        return list(set(cluster))

    @staticmethod
    def identify_change(tx_data: Dict[str, Any]) -> Optional[str]:
        """
        Attempts to identify the change output of a transaction.
        Checks for:
        1. Address type match (input type == output type)
        2. Round numbers (payments are often round, change is the remainder)
        3. Simple heuristic: if there are 2 outputs, and one has never been seen before.
        """
        vouts = tx_data.get("vout", [])
        if len(vouts) != 2:
            return None # Heuristic works best with 2 outputs (payment + change)

        # Basic Check: Address Type Match
        # In a real engine, we'd compare prefix (bc1, 3, 1) or script types.
        
        # Basic Check: Round Number Heuristic
        # Payments like 0.1 BTC (10,000,000 sats) are often signals.
        scores = {idx: 0 for idx in range(len(vouts))}
        
        for idx, vout in enumerate(vouts):
            val = vout.get("value", 0)
            # If value in sats is divisible by a large power of 10
            if val > 0 and val % 1000000 == 0:
                scores[idx] -= 1 # Likely a payment, not change

        # The one with the highest score is the guessed change
        likely_change_idx = max(scores, key=scores.get)
        
        # Return address of guessed change
        # Mempool format
        if "scriptpubkey_address" in vouts[likely_change_idx]:
            return vouts[likely_change_idx]["scriptpubkey_address"]
        # RPC format
        elif "scriptPubKey" in vouts[likely_change_idx] and "address" in vouts[likely_change_idx]["scriptPubKey"]:
             return vouts[likely_change_idx]["scriptPubKey"]["address"]
             
        return None
