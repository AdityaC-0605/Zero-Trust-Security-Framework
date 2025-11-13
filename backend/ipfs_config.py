"""
IPFS Configuration for Distributed Storage
Handles large audit data storage on IPFS
"""

import os
import ipfshttpclient
from dotenv import load_dotenv

load_dotenv()

# IPFS Configuration
IPFS_ENABLED = os.getenv('IPFS_ENABLED', 'true').lower() == 'true'
IPFS_HOST = os.getenv('IPFS_HOST', 'localhost')
IPFS_PORT = int(os.getenv('IPFS_PORT', '5001'))
IPFS_PROTOCOL = os.getenv('IPFS_PROTOCOL', 'http')

# IPFS Client
ipfs_client = None

def init_ipfs():
    """Initialize IPFS client"""
    global ipfs_client
    
    if not IPFS_ENABLED:
        print("IPFS is disabled")
        return None
    
    try:
        ipfs_client = ipfshttpclient.connect(
            f'/dns/{IPFS_HOST}/tcp/{IPFS_PORT}/{IPFS_PROTOCOL}'
        )
        
        # Test connection
        version = ipfs_client.version()
        print(f"Connected to IPFS node version {version['Version']}")
        
        return ipfs_client
    except Exception as e:
        print(f"IPFS initialization error: {e}")
        print("IPFS features will be disabled")
        return None


def get_ipfs_client():
    """Get IPFS client instance"""
    return ipfs_client


def is_ipfs_available():
    """Check if IPFS is available"""
    return ipfs_client is not None


def add_to_ipfs(data):
    """
    Add data to IPFS
    
    Args:
        data: String or bytes to store on IPFS
        
    Returns:
        str: IPFS content identifier (CID) or None if failed
    """
    if not ipfs_client:
        return None
    
    try:
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        result = ipfs_client.add_bytes(data)
        return result
    except Exception as e:
        print(f"Error adding to IPFS: {e}")
        return None


def get_from_ipfs(cid):
    """
    Retrieve data from IPFS
    
    Args:
        cid: IPFS content identifier
        
    Returns:
        bytes: Retrieved data or None if failed
    """
    if not ipfs_client:
        return None
    
    try:
        data = ipfs_client.cat(cid)
        return data
    except Exception as e:
        print(f"Error retrieving from IPFS: {e}")
        return None


def pin_to_ipfs(cid):
    """
    Pin content to ensure it stays on the node
    
    Args:
        cid: IPFS content identifier to pin
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not ipfs_client:
        return False
    
    try:
        ipfs_client.pin.add(cid)
        return True
    except Exception as e:
        print(f"Error pinning to IPFS: {e}")
        return False


def unpin_from_ipfs(cid):
    """
    Unpin content from the node
    
    Args:
        cid: IPFS content identifier to unpin
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not ipfs_client:
        return False
    
    try:
        ipfs_client.pin.rm(cid)
        return True
    except Exception as e:
        print(f"Error unpinning from IPFS: {e}")
        return False


def get_ipfs_stats():
    """
    Get IPFS node statistics
    
    Returns:
        dict: Node statistics or None if failed
    """
    if not ipfs_client:
        return None
    
    try:
        stats = {
            'version': ipfs_client.version(),
            'id': ipfs_client.id(),
            'repo_stats': ipfs_client.repo.stat()
        }
        return stats
    except Exception as e:
        print(f"Error getting IPFS stats: {e}")
        return None
