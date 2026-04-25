import pytest
from unittest.mock import patch, MagicMock
from app.services.encryption_service import EncryptionService
from app.services.auth_policy import AuthPolicyEnforcer
import time
import datetime

def test_encryption_service_reversibility():
    service = EncryptionService()
    secret = "my-secret-pii-data"
    encrypted = service.encrypt(secret)
    
    assert encrypted != secret
    assert len(encrypted) > 10
    
    decrypted = service.decrypt(encrypted)
    assert decrypted == secret

def test_password_length_enforcement():
    with patch("app.services.auth_policy.firestore.client"):
        enforcer = AuthPolicyEnforcer()
    assert not enforcer.validate_password("short")
    assert enforcer.validate_password("this_is_a_very_long_password")

def test_lockout_policy():
    with patch("app.services.auth_policy.firestore.client"):
        enforcer = AuthPolicyEnforcer()
    
    doc_mock = MagicMock()
    doc_mock.exists = True
    now = datetime.datetime.now(datetime.timezone.utc)
    doc_mock.to_dict.return_value = {
        "count": 4,
        "first_failure": now.isoformat(),
        "locked": False
    }
    
    db_mock = MagicMock()
    db_mock.collection().document().get.return_value = doc_mock
    enforcer.db = db_mock
    
    locked = enforcer.track_failed_attempt("user_x")
    assert locked is True
    
    db_mock.collection().document().set.assert_called_with({
        "count": 5, 
        "first_failure": now.isoformat(),
        "locked": True
    })
