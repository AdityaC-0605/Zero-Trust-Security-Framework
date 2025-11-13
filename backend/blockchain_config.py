"""
Blockchain Configuration for Immutable Audit Trail
Handles Ethereum integration and smart contract deployment
"""

import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

# Blockchain Configuration
BLOCKCHAIN_ENABLED = os.getenv('BLOCKCHAIN_ENABLED', 'true').lower() == 'true'
BLOCKCHAIN_PROVIDER_URL = os.getenv('BLOCKCHAIN_PROVIDER_URL', 'http://localhost:8545')
BLOCKCHAIN_NETWORK_ID = int(os.getenv('BLOCKCHAIN_NETWORK_ID', '1337'))
BLOCKCHAIN_CONTRACT_ADDRESS = os.getenv('BLOCKCHAIN_CONTRACT_ADDRESS', '')
BLOCKCHAIN_PRIVATE_KEY = os.getenv('BLOCKCHAIN_PRIVATE_KEY', '')

# Initialize Web3
w3 = None
contract = None

def init_blockchain():
    """Initialize blockchain connection"""
    global w3, contract
    
    if not BLOCKCHAIN_ENABLED:
        print("Blockchain is disabled")
        return None
    
    try:
        w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_PROVIDER_URL))
        
        if w3.is_connected():
            print(f"Connected to blockchain at {BLOCKCHAIN_PROVIDER_URL}")
            print(f"Network ID: {BLOCKCHAIN_NETWORK_ID}")
            print(f"Latest block: {w3.eth.block_number}")
            
            # Load contract if address is configured
            if BLOCKCHAIN_CONTRACT_ADDRESS:
                contract = load_contract(BLOCKCHAIN_CONTRACT_ADDRESS)
                print(f"Loaded contract at {BLOCKCHAIN_CONTRACT_ADDRESS}")
            
            return w3
        else:
            print("Failed to connect to blockchain")
            return None
    except Exception as e:
        print(f"Blockchain initialization error: {e}")
        return None


def load_contract(contract_address):
    """Load smart contract instance"""
    if not w3:
        return None
    
    # Contract ABI (will be generated after deployment)
    contract_abi = get_contract_abi()
    
    try:
        contract = w3.eth.contract(
            address=Web3.to_checksum_address(contract_address),
            abi=contract_abi
        )
        return contract
    except Exception as e:
        print(f"Error loading contract: {e}")
        return None


def get_contract_abi():
    """Get contract ABI"""
    # This will be populated after smart contract compilation
    return [
        {
            "inputs": [
                {"internalType": "address", "name": "userId", "type": "address"},
                {"internalType": "string", "name": "eventType", "type": "string"},
                {"internalType": "bytes32", "name": "dataHash", "type": "bytes32"},
                {"internalType": "string", "name": "ipfsHash", "type": "string"}
            ],
            "name": "recordEvent",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "uint256", "name": "eventId", "type": "uint256"},
                {"internalType": "bytes32", "name": "dataHash", "type": "bytes32"}
            ],
            "name": "verifyEvent",
            "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "name": "auditTrail",
            "outputs": [
                {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
                {"internalType": "address", "name": "userId", "type": "address"},
                {"internalType": "string", "name": "eventType", "type": "string"},
                {"internalType": "bytes32", "name": "dataHash", "type": "bytes32"},
                {"internalType": "string", "name": "ipfsHash", "type": "string"}
            ],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "eventCount",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "anonymous": False,
            "inputs": [
                {"indexed": True, "internalType": "uint256", "name": "eventId", "type": "uint256"},
                {"indexed": False, "internalType": "bytes32", "name": "dataHash", "type": "bytes32"}
            ],
            "name": "EventRecorded",
            "type": "event"
        }
    ]


def get_web3_instance():
    """Get Web3 instance"""
    return w3


def get_contract_instance():
    """Get contract instance"""
    return contract


def is_blockchain_available():
    """Check if blockchain is available"""
    return w3 is not None and w3.is_connected()
