"""Blockchain Service - Immutable audit trail"""
import os
import hashlib
import json
from datetime import datetime
from blockchain_config import get_web3_instance, get_contract_instance, is_blockchain_available
from ipfs_config import add_to_ipfs, is_ipfs_available

class BlockchainService:
    def __init__(self):
        self.enabled = os.getenv('BLOCKCHAIN_ENABLED', 'false').lower() == 'true'
        self.w3 = get_web3_instance()
        self.contract = get_contract_instance()
    
    def record_event(self, user_id, event_type, event_data):
        """Record security event to blockchain"""
        if not self.enabled or not is_blockchain_available():
            return None
        
        try:
            # Create data hash
            data_str = json.dumps(event_data, sort_keys=True)
            data_hash = hashlib.sha256(data_str.encode()).hexdigest()
            
            # Store large data in IPFS
            ipfs_hash = ""
            if is_ipfs_available() and len(data_str) > 1000:
                ipfs_hash = add_to_ipfs(data_str) or ""
            
            # Record to blockchain
            if self.contract:
                tx_hash = self.contract.functions.recordEvent(
                    user_id,
                    event_type,
                    bytes.fromhex(data_hash),
                    ipfs_hash
                ).transact()
                
                return {
                    'transaction_hash': tx_hash.hex(),
                    'data_hash': data_hash,
                    'ipfs_hash': ipfs_hash,
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            return None
        except Exception as e:
            print(f"Blockchain error: {e}")
            return None
    
    def verify_event(self, event_id, expected_data):
        """Verify event integrity"""
        if not self.enabled or not self.contract:
            return False
        
        try:
            data_str = json.dumps(expected_data, sort_keys=True)
            expected_hash = hashlib.sha256(data_str.encode()).hexdigest()
            
            is_valid = self.contract.functions.verifyEvent(
                event_id,
                bytes.fromhex(expected_hash)
            ).call()
            
            return is_valid
        except:
            return False

blockchain_service = BlockchainService()
