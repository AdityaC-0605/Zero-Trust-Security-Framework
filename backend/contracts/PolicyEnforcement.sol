// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title PolicyEnforcement
 * @dev Smart contract for immutable audit trail of security events
 */
contract PolicyEnforcement {
    
    struct AuditEvent {
        uint256 timestamp;
        address userId;
        string eventType;
        bytes32 dataHash;
        string ipfsHash;
    }
    
    // Mapping from event ID to audit event
    mapping(uint256 => AuditEvent) public auditTrail;
    
    // Total number of events recorded
    uint256 public eventCount;
    
    // Event emitted when a new audit event is recorded
    event EventRecorded(uint256 indexed eventId, bytes32 dataHash);
    
    // Event emitted when an event is verified
    event EventVerified(uint256 indexed eventId, bool isValid);
    
    /**
     * @dev Record a new audit event
     * @param userId Address of the user associated with the event
     * @param eventType Type of security event (access_grant, access_deny, policy_change, admin_action)
     * @param dataHash SHA-256 hash of the event data
     * @param ipfsHash IPFS content identifier for large data
     * @return eventId The ID of the recorded event
     */
    function recordEvent(
        address userId,
        string memory eventType,
        bytes32 dataHash,
        string memory ipfsHash
    ) public returns (uint256) {
        eventCount++;
        
        auditTrail[eventCount] = AuditEvent({
            timestamp: block.timestamp,
            userId: userId,
            eventType: eventType,
            dataHash: dataHash,
            ipfsHash: ipfsHash
        });
        
        emit EventRecorded(eventCount, dataHash);
        
        return eventCount;
    }
    
    /**
     * @dev Verify the integrity of an audit event
     * @param eventId ID of the event to verify
     * @param dataHash Expected hash of the event data
     * @return bool True if the hash matches, false otherwise
     */
    function verifyEvent(uint256 eventId, bytes32 dataHash) 
        public 
        view 
        returns (bool) 
    {
        require(eventId > 0 && eventId <= eventCount, "Invalid event ID");
        return auditTrail[eventId].dataHash == dataHash;
    }
    
    /**
     * @dev Get audit event details
     * @param eventId ID of the event to retrieve
     * @return timestamp Time when event was recorded
     * @return userId User associated with the event
     * @return eventType Type of security event
     * @return dataHash Hash of the event data
     * @return ipfsHash IPFS content identifier
     */
    function getEvent(uint256 eventId) 
        public 
        view 
        returns (
            uint256 timestamp,
            address userId,
            string memory eventType,
            bytes32 dataHash,
            string memory ipfsHash
        ) 
    {
        require(eventId > 0 && eventId <= eventCount, "Invalid event ID");
        
        AuditEvent memory evt = auditTrail[eventId];
        return (
            evt.timestamp,
            evt.userId,
            evt.eventType,
            evt.dataHash,
            evt.ipfsHash
        );
    }
    
    /**
     * @dev Get total number of recorded events
     * @return uint256 Total event count
     */
    function getEventCount() public view returns (uint256) {
        return eventCount;
    }
    
    /**
     * @dev Get events in a range
     * @param startId Starting event ID
     * @param endId Ending event ID
     * @return eventIds Array of event IDs in the range
     */
    function getEventRange(uint256 startId, uint256 endId) 
        public 
        view 
        returns (uint256[] memory eventIds) 
    {
        require(startId > 0 && startId <= eventCount, "Invalid start ID");
        require(endId >= startId && endId <= eventCount, "Invalid end ID");
        
        uint256 rangeSize = endId - startId + 1;
        eventIds = new uint256[](rangeSize);
        
        for (uint256 i = 0; i < rangeSize; i++) {
            eventIds[i] = startId + i;
        }
        
        return eventIds;
    }
}
