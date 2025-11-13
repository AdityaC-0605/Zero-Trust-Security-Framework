"""
Contextual Intelligence Service
Evaluates device health, network security, time/location for access decisions
"""

import os
import requests
from datetime import datetime, time
from typing import Dict, Optional
from app.firebase_config import db

# Configuration
CONTEXT_EVALUATION_ENABLED = os.getenv('CONTEXT_EVALUATION_ENABLED', 'false').lower() == 'true'
DEVICE_HEALTH_WEIGHT = float(os.getenv('DEVICE_HEALTH_WEIGHT', '0.25'))
NETWORK_SECURITY_WEIGHT = float(os.getenv('NETWORK_SECURITY_WEIGHT', '0.25'))
TIME_APPROPRIATENESS_WEIGHT = float(os.getenv('TIME_APPROPRIATENESS_WEIGHT', '0.20'))
LOCATION_RISK_WEIGHT = float(os.getenv('LOCATION_RISK_WEIGHT', '0.15'))
HISTORICAL_TRUST_WEIGHT = float(os.getenv('HISTORICAL_TRUST_WEIGHT', '0.15'))

ABUSEIPDB_API_KEY = os.getenv('ABUSEIPDB_API_KEY', '')
IPQUALITYSCORE_API_KEY = os.getenv('IPQUALITYSCORE_API_KEY', '')

try:
    import geoip2.database
    GEOIP_AVAILABLE = True
    GEOIP_DB_PATH = os.getenv('GEOIP2_DATABASE_PATH', './geoip2/GeoLite2-City.mmdb')
except ImportError:
    GEOIP_AVAILABLE = False


class ContextualIntelligence:
    """Service for contextual intelligence evaluation"""
    
    def __init__(self):
        self.geoip_reader = None
        if GEOIP_AVAILABLE and os.path.exists(GEOIP_DB_PATH):
            try:
                self.geoip_reader = geoip2.database.Reader(GEOIP_DB_PATH)
            except:
                pass
    
    def evaluate_device_health(self, device_info: Dict) -> Dict:
        """Evaluate device health score (0-100)"""
        scores = {}
        
        # OS version check (30%)
        os_version = device_info.get('os_version', '')
        os_updated = device_info.get('os_updated', False)
        scores['os_version'] = 100 if os_updated else 50
        
        # Security software (25%)
        has_antivirus = device_info.get('has_antivirus', False)
        antivirus_updated = device_info.get('antivirus_updated', False)
        scores['security_software'] = 100 if (has_antivirus and antivirus_updated) else (50 if has_antivirus else 0)
        
        # Encryption (20%)
        is_encrypted = device_info.get('is_encrypted', False)
        scores['encryption'] = 100 if is_encrypted else 0
        
        # Known device (15%)
        is_known = device_info.get('is_known', False)
        scores['known_device'] = 100 if is_known else 30
        
        # Policy compliance (10%)
        is_compliant = device_info.get('is_compliant', True)
        scores['compliance'] = 100 if is_compliant else 0
        
        # Calculate weighted score
        total_score = (
            scores['os_version'] * 0.30 +
            scores['security_software'] * 0.25 +
            scores['encryption'] * 0.20 +
            scores['known_device'] * 0.15 +
            scores['compliance'] * 0.10
        )
        
        return {
            'device_health_score': round(total_score, 2),
            'component_scores': scores,
            'risk_level': 'low' if total_score >= 70 else ('medium' if total_score >= 40 else 'high')
        }
    
    def evaluate_network_security(self, network_info: Dict) -> Dict:
        """Evaluate network security score (0-100)"""
        scores = {}
        ip_address = network_info.get('ip_address')
        
        # Network type (35%)
        network_type = network_info.get('network_type', 'unknown')
        type_scores = {'campus_wifi': 100, 'vpn': 90, 'home': 60, 'public': 20, 'unknown': 40}
        scores['network_type'] = type_scores.get(network_type, 40)
        
        # VPN usage (25%)
        using_vpn = network_info.get('using_vpn', False)
        scores['vpn_usage'] = 100 if using_vpn else 30
        
        # IP reputation (20%)
        ip_reputation = self._check_ip_reputation(ip_address) if ip_address else 50
        scores['ip_reputation'] = ip_reputation
        
        # Geographic location (20%)
        location_risk = self._evaluate_location_risk(ip_address) if ip_address else 50
        scores['location_risk'] = location_risk
        
        # Calculate weighted score
        total_score = (
            scores['network_type'] * 0.35 +
            scores['vpn_usage'] * 0.25 +
            scores['ip_reputation'] * 0.20 +
            scores['location_risk'] * 0.20
        )
        
        return {
            'network_security_score': round(total_score, 2),
            'component_scores': scores,
            'risk_level': 'low' if total_score >= 70 else ('medium' if total_score >= 40 else 'high')
        }
    
    def evaluate_time_appropriateness(self, user_id: str, access_time: datetime = None) -> Dict:
        """Evaluate time appropriateness (0-100)"""
        if not access_time:
            access_time = datetime.utcnow()
        
        hour = access_time.hour
        day_of_week = access_time.weekday()
        
        # Get user's typical access times
        typical_hours = self._get_typical_access_hours(user_id)
        
        # Time of day score (60%)
        if 6 <= hour < 22:  # Business hours
            time_score = 100
        elif 22 <= hour or hour < 2:  # Evening
            time_score = 60
        else:  # 2-6 AM
            time_score = 20
        
        # Day of week score (40%)
        if day_of_week < 5:  # Weekday
            day_score = 100
        else:  # Weekend
            day_score = 60
        
        # Check against typical patterns
        is_typical = hour in typical_hours
        pattern_bonus = 20 if is_typical else 0
        
        total_score = min(time_score * 0.60 + day_score * 0.40 + pattern_bonus, 100)
        
        return {
            'time_appropriateness_score': round(total_score, 2),
            'hour': hour,
            'day_of_week': day_of_week,
            'is_typical_time': is_typical,
            'risk_level': 'low' if total_score >= 70 else ('medium' if total_score >= 40 else 'high')
        }
    
    def detect_impossible_travel(self, user_id: str, current_location: Dict, current_time: datetime) -> Dict:
        """Detect impossible travel scenarios"""
        last_access = self._get_last_access_location(user_id)
        
        if not last_access:
            return {'impossible_travel': False, 'reason': 'No previous location data'}
        
        # Calculate distance and time difference
        distance_km = self._calculate_distance(
            last_access.get('latitude'), last_access.get('longitude'),
            current_location.get('latitude'), current_location.get('longitude')
        )
        
        time_diff_hours = (current_time - last_access.get('timestamp')).total_seconds() / 3600
        
        # Maximum realistic travel speed (800 km/h for air travel)
        max_speed_kmh = 800
        required_speed = distance_km / time_diff_hours if time_diff_hours > 0 else 0
        
        is_impossible = required_speed > max_speed_kmh and time_diff_hours < 12
        
        return {
            'impossible_travel': is_impossible,
            'distance_km': round(distance_km, 2),
            'time_diff_hours': round(time_diff_hours, 2),
            'required_speed_kmh': round(required_speed, 2),
            'max_realistic_speed': max_speed_kmh,
            'risk_level': 'critical' if is_impossible else 'low'
        }
    
    def calculate_overall_context_score(self, user_id: str, device_info: Dict, 
                                       network_info: Dict, access_time: datetime = None) -> Dict:
        """Calculate overall context score with weighted components"""
        
        # Evaluate all components
        device_eval = self.evaluate_device_health(device_info)
        network_eval = self.evaluate_network_security(network_info)
        time_eval = self.evaluate_time_appropriateness(user_id, access_time)
        
        # Get historical trust score
        historical_trust = self._get_historical_trust_score(user_id)
        
        # Calculate weighted overall score
        overall_score = (
            device_eval['device_health_score'] * DEVICE_HEALTH_WEIGHT +
            network_eval['network_security_score'] * NETWORK_SECURITY_WEIGHT +
            time_eval['time_appropriateness_score'] * TIME_APPROPRIATENESS_WEIGHT +
            self._evaluate_location_risk(network_info.get('ip_address')) * LOCATION_RISK_WEIGHT +
            historical_trust * HISTORICAL_TRUST_WEIGHT
        )
        
        # Determine if step-up authentication is needed
        requires_step_up = overall_score < 60
        
        return {
            'overall_context_score': round(overall_score, 2),
            'requires_step_up_auth': requires_step_up,
            'component_scores': {
                'device_health': device_eval['device_health_score'],
                'network_security': network_eval['network_security_score'],
                'time_appropriateness': time_eval['time_appropriateness_score'],
                'location_risk': self._evaluate_location_risk(network_info.get('ip_address')),
                'historical_trust': historical_trust
            },
            'risk_level': 'low' if overall_score >= 70 else ('medium' if overall_score >= 50 else 'high'),
            'recommendations': self._generate_recommendations(overall_score, device_eval, network_eval, time_eval)
        }
    
    def _check_ip_reputation(self, ip_address: str) -> float:
        """Check IP reputation using external APIs"""
        if not ip_address:
            return 50
        
        scores = []
        
        # AbuseIPDB check
        if ABUSEIPDB_API_KEY:
            try:
                response = requests.get(
                    'https://api.abuseipdb.com/api/v2/check',
                    headers={'Key': ABUSEIPDB_API_KEY, 'Accept': 'application/json'},
                    params={'ipAddress': ip_address, 'maxAgeInDays': 90},
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json().get('data', {})
                    abuse_score = data.get('abuseConfidenceScore', 0)
                    scores.append(100 - abuse_score)
            except:
                pass
        
        # IPQualityScore check
        if IPQUALITYSCORE_API_KEY:
            try:
                response = requests.get(
                    f'https://ipqualityscore.com/api/json/ip/{IPQUALITYSCORE_API_KEY}/{ip_address}',
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    fraud_score = data.get('fraud_score', 0)
                    scores.append(100 - fraud_score)
            except:
                pass
        
        return sum(scores) / len(scores) if scores else 70
    
    def _evaluate_location_risk(self, ip_address: str) -> float:
        """Evaluate geographic location risk"""
        if not ip_address or not self.geoip_reader:
            return 70
        
        try:
            response = self.geoip_reader.city(ip_address)
            country = response.country.iso_code
            
            # High-risk countries (simplified)
            high_risk_countries = ['CN', 'RU', 'KP', 'IR']
            medium_risk_countries = ['VN', 'IN', 'BR']
            
            if country in high_risk_countries:
                return 30
            elif country in medium_risk_countries:
                return 60
            else:
                return 90
        except:
            return 70
    
    def _get_typical_access_hours(self, user_id: str) -> set:
        """Get user's typical access hours from history"""
        try:
            query = db.collection('audit_logs')\
                     .where('user_id', '==', user_id)\
                     .where('action', '==', 'login')\
                     .where('result', '==', 'success')\
                     .limit(100)
            
            docs = query.stream()
            hours = set()
            
            for doc in docs:
                data = doc.to_dict()
                timestamp = data.get('timestamp')
                if timestamp:
                    hours.add(timestamp.hour)
            
            return hours if hours else set(range(6, 22))
        except:
            return set(range(6, 22))
    
    def _get_historical_trust_score(self, user_id: str) -> float:
        """Calculate historical trust score based on past behavior"""
        try:
            query = db.collection('audit_logs')\
                     .where('user_id', '==', user_id)\
                     .limit(100)
            
            docs = query.stream()
            total = 0
            success = 0
            
            for doc in docs:
                data = doc.to_dict()
                total += 1
                if data.get('result') == 'success':
                    success += 1
            
            return (success / total * 100) if total > 0 else 70
        except:
            return 70
    
    def _get_last_access_location(self, user_id: str) -> Optional[Dict]:
        """Get user's last access location"""
        try:
            query = db.collection('audit_logs')\
                     .where('user_id', '==', user_id)\
                     .where('action', '==', 'login')\
                     .order_by('timestamp', direction='DESCENDING')\
                     .limit(1)
            
            docs = query.stream()
            for doc in docs:
                data = doc.to_dict()
                return {
                    'latitude': data.get('latitude'),
                    'longitude': data.get('longitude'),
                    'timestamp': data.get('timestamp')
                }
            return None
        except:
            return None
    
    def _calculate_distance(self, lat1, lon1, lat2, lon2) -> float:
        """Calculate distance between two coordinates in km"""
        if not all([lat1, lon1, lat2, lon2]):
            return 0
        
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth radius in km
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    def _generate_recommendations(self, overall_score, device_eval, network_eval, time_eval) -> list:
        """Generate security recommendations based on context"""
        recommendations = []
        
        if device_eval['device_health_score'] < 60:
            recommendations.append('Update device security software and OS')
        
        if network_eval['network_security_score'] < 60:
            recommendations.append('Use VPN or secure network connection')
        
        if time_eval['time_appropriateness_score'] < 60:
            recommendations.append('Access during typical business hours when possible')
        
        if overall_score < 50:
            recommendations.append('Enable step-up authentication for this session')
        
        return recommendations


# Global service instance
contextual_intelligence = ContextualIntelligence()
