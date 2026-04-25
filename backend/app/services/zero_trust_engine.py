import os
from datetime import datetime
from typing import Dict, Any, Tuple
from app.firebase_config import get_firestore_client

class ZeroTrustEngine:
    def __init__(self):
        self.db = get_firestore_client()
        self.AUTO_APPROVE_THRESHOLD = 80
        self.REQUIRE_MFA_THRESHOLD = 50
    
    def evaluate_access(self, user: Dict[str, Any], device: Dict[str, Any], context: Dict[str, Any], resource: str) -> Tuple[bool, str, int]:
        """
        True Zero Trust Central Policy Engine
        Deny by default. Allow only if ALL conditions pass.
        
        Args:
            user (dict): User identity data {id, role, etc.}
            device (dict): Device context {id, trust_score, mismatch}
            context (dict): Request context {ip, time, user_agent, risk}
            resource (str): The requested resource
            
        Returns:
            Tuple[bool, str, int]: (is_allowed, reason, risk_score)
        """
        # 0. Deny by default
        is_allowed = False
        reason = "Access denied: Implicit deny"
        risk_score = 100  # 100 = Highest risk
        
        # 1. Identity Check
        if not user or not user.get('uid'):
            return False, "Access denied: Unverified identity", 100
        
        # 2. Device Trust Verification
        # True Zero trust requires trusted devices.
        if not device or device.get('is_mismatch', True):
            return False, "Access denied: Device fingerprint mismatch or unknown", 95
            
        device_trust = device.get('trust_score', 0)
        if device_trust < 50:
            return False, f"Access denied: Device trust score too low ({device_trust})", 85
            
        # 3. Context Validation (Time, IP, Anomaly)
        # e.g., enforce IP whitelists or time restrictions based on role
        if context.get('is_anomalous_ip', False):
            return False, "Access denied: Login from impossible travel / anomalous IP", 90
            
        # 4. Policy / Role check for resource
        allowed = self._check_role_resource_policy(user.get('role', 'user'), resource)
        if not allowed:
            return False, f"Access denied: Insufficient privileges for resource {resource}", 75
            
        # 5. Risk Calculation
        # Lower risk is better.
        # If device trust is 100, risk is 0. If device trust is 50, risk is 50.
        base_risk = 100 - device_trust
        risk_score = min(100, max(0, base_risk + context.get('risk_modifier', 0)))
        
        if risk_score > self.REQUIRE_MFA_THRESHOLD:
            # Need MFA or block
            if context.get('mfa_verified', False):
                is_allowed = True
                reason = "Access granted with MFA override"
            else:
                return False, "Access denied: Step-up authentication (MFA) required due to risk", risk_score
        else:
            is_allowed = True
            reason = "Access granted"
            
        return is_allowed, reason, risk_score
        
    def _check_role_resource_policy(self, role: str, resource: str) -> bool:
        """Fetch policy from DB to see if role can access resource."""
        # For simplicity, if admin, allow all. If wildcard policy matches, allow.
        if role == 'admin':
            return True
            
        if not self.db:
            return False
            
        policies_ref = self.db.collection('policies')
        query = policies_ref.where('isActive', '==', True)
        
        for doc in query.stream():
            policy = doc.to_dict()
            for rule in policy.get('rules', []):
                req_resource = rule.get('resourceType', '')
                allowed_roles = rule.get('allowedRoles', [])
                if (req_resource == '*' or req_resource in resource or resource in req_resource) and (role in allowed_roles or '*' in allowed_roles):
                    return True
                    
        return False

zero_trust_engine = ZeroTrustEngine()
