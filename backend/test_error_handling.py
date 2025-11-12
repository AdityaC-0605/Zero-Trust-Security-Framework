"""
Test Error Handling and Validation
Tests for the enhanced error handling system
"""

import pytest
from app.utils.error_handler import (
    AppError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    RateLimitError,
    create_error_response,
    validate_required_fields,
    validate_field_length,
    validate_enum,
    validate_email,
    validate_word_count
)


def test_validation_error():
    """Test ValidationError creation"""
    error = ValidationError("Invalid email format", field="email")
    
    assert error.message == "Invalid email format"
    assert error.code == "VALIDATION_ERROR"
    assert error.status_code == 400
    assert error.details['field'] == "email"


def test_authentication_error():
    """Test AuthenticationError creation"""
    error = AuthenticationError("Invalid credentials")
    
    assert error.message == "Invalid credentials"
    assert error.code == "AUTH_FAILED"
    assert error.status_code == 401


def test_authorization_error():
    """Test AuthorizationError creation"""
    error = AuthorizationError("Access denied")
    
    assert error.message == "Access denied"
    assert error.code == "INSUFFICIENT_PERMISSIONS"
    assert error.status_code == 403


def test_not_found_error():
    """Test NotFoundError creation"""
    error = NotFoundError("User not found", resource_type="user")
    
    assert error.message == "User not found"
    assert error.code == "RESOURCE_NOT_FOUND"
    assert error.status_code == 404
    assert error.details['resourceType'] == "user"


def test_rate_limit_error():
    """Test RateLimitError creation"""
    error = RateLimitError()
    
    assert error.code == "RATE_LIMIT_EXCEEDED"
    assert error.status_code == 429


def test_create_error_response_app_error():
    """Test creating error response from AppError"""
    error = ValidationError("Invalid input", field="username")
    response, status_code = create_error_response(error, include_details=True)
    
    assert response['success'] is False
    assert response['error']['code'] == "VALIDATION_ERROR"
    assert response['error']['message'] == "Invalid input"
    assert response['error']['details']['field'] == "username"
    assert status_code == 400


def test_create_error_response_generic_error():
    """Test creating error response from generic exception"""
    error = Exception("Something went wrong")
    response, status_code = create_error_response(error, include_details=True)
    
    assert response['success'] is False
    assert response['error']['code'] == "INTERNAL_ERROR"
    assert response['error']['message'] == "Something went wrong"
    assert status_code == 500


def test_validate_required_fields_success():
    """Test validate_required_fields with valid data"""
    data = {
        'email': 'test@example.com',
        'password': 'password123',
        'name': 'Test User'
    }
    required_fields = ['email', 'password', 'name']
    
    # Should not raise exception
    validate_required_fields(data, required_fields)


def test_validate_required_fields_missing():
    """Test validate_required_fields with missing fields"""
    data = {
        'email': 'test@example.com'
    }
    required_fields = ['email', 'password', 'name']
    
    with pytest.raises(ValidationError) as exc_info:
        validate_required_fields(data, required_fields)
    
    assert 'password' in exc_info.value.message
    assert 'name' in exc_info.value.message


def test_validate_field_length_success():
    """Test validate_field_length with valid length"""
    validate_field_length("Hello World", "message", min_length=5, max_length=20)


def test_validate_field_length_too_short():
    """Test validate_field_length with too short value"""
    with pytest.raises(ValidationError) as exc_info:
        validate_field_length("Hi", "message", min_length=5)
    
    assert "at least 5 characters" in exc_info.value.message


def test_validate_field_length_too_long():
    """Test validate_field_length with too long value"""
    with pytest.raises(ValidationError) as exc_info:
        validate_field_length("This is a very long message", "message", max_length=10)
    
    assert "must not exceed 10 characters" in exc_info.value.message


def test_validate_enum_success():
    """Test validate_enum with valid value"""
    validate_enum("student", "role", ["student", "faculty", "admin"])


def test_validate_enum_invalid():
    """Test validate_enum with invalid value"""
    with pytest.raises(ValidationError) as exc_info:
        validate_enum("invalid", "role", ["student", "faculty", "admin"])
    
    assert "must be one of" in exc_info.value.message


def test_validate_email_success():
    """Test validate_email with valid email"""
    validate_email("test@example.com")


def test_validate_email_invalid():
    """Test validate_email with invalid email"""
    with pytest.raises(ValidationError) as exc_info:
        validate_email("invalid-email")
    
    assert "Invalid email format" in exc_info.value.message


def test_validate_word_count_success():
    """Test validate_word_count with valid word count"""
    text = "This is a test message with enough words"
    validate_word_count(text, "intent", min_words=5)


def test_validate_word_count_too_few():
    """Test validate_word_count with too few words"""
    text = "Too short"
    
    with pytest.raises(ValidationError) as exc_info:
        validate_word_count(text, "intent", min_words=5)
    
    assert "at least 5 words" in exc_info.value.message


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
