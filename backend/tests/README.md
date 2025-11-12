# Integration and End-to-End Test Suite

This directory contains comprehensive integration and end-to-end tests for the Zero Trust Security Framework.

## Test Structure

### Test Files

- `test_integration_auth_flow.py` - Authentication flow tests (signup, login, MFA, logout)
- `test_integration_access_request_flow.py` - Access request submission and evaluation tests
- `test_integration_admin_operations.py` - Admin user management, audit logs, and analytics tests
- `test_integration_policy_config.py` - Policy configuration and application tests
- `test_integration_protected_routes.py` - Route protection and authorization tests
- `test_e2e_complete_flows.py` - Complete end-to-end user journey tests

### Test Markers

Tests are marked with pytest markers for selective execution:

- `@pytest.mark.integration` - Integration tests that test multiple components together
- `@pytest.mark.e2e` - End-to-end tests that test complete user flows
- `@pytest.mark.unit` - Unit tests for individual components
- `@pytest.mark.slow` - Tests that take longer to run

## Running Tests

### Prerequisites

1. Install test dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure environment variables are set in `.env` file

### Run All Tests

```bash
# From backend directory
pytest tests/ -v
```

### Run Specific Test Categories

```bash
# Integration tests only
pytest tests/ -v -m integration

# E2E tests only
pytest tests/ -v -m e2e

# Specific test file
pytest tests/test_integration_auth_flow.py -v

# Specific test class
pytest tests/test_integration_auth_flow.py::TestAuthenticationFlow -v

# Specific test method
pytest tests/test_integration_auth_flow.py::TestAuthenticationFlow::test_login_flow -v
```

### Using the Test Runner Script

```bash
python run_integration_tests.py
```

This interactive script allows you to select which test suite to run.

## Test Coverage

### Authentication Flow Tests

- User signup with validation
- User login with Firebase token verification
- MFA setup and verification
- Account lockout after failed attempts
- Session refresh
- Logout functionality
- Edge cases (invalid credentials, missing fields, weak passwords)

### Access Request Flow Tests

- Access request submission with validation
- Policy engine evaluation (high/medium/low confidence)
- Request history retrieval
- Specific request details
- Request resubmission
- Rate limiting
- Edge cases (invalid intent, missing fields, unauthorized access)

### Admin Operations Tests

- User management (list, update, deactivate)
- Role modification with audit logging
- Admin self-deletion prevention
- User filtering and search
- Audit log retrieval with filtering
- Analytics generation with time ranges
- Edge cases (non-existent users, invalid roles)

### Policy Configuration Tests

- Policy creation and updates
- Policy retrieval
- Policy validation (confidence thresholds, allowed roles)
- Policy matching by resource type
- Policy priority ordering
- Time restrictions
- Edge cases (missing fields, invalid values)

### Protected Routes Tests

- Authentication requirement enforcement
- Token validation (valid, expired, malformed)
- Role-based access control
- CSRF protection
- Authorization middleware
- Payload size limits
- CORS and security headers
- Edge cases (non-existent routes, wrong methods)

### End-to-End Flow Tests

- Complete student flow (signup → login → request → history)
- Complete admin flow (login → manage users → logs → policy)
- MFA-enabled user flow
- Error recovery flows
- Request resubmission after denial

## Test Configuration

### Fixtures (conftest.py)

- `app` - Flask test application
- `client` - Flask test client
- `mock_firestore` - Mocked Firestore client
- `mock_firebase_auth` - Mocked Firebase Auth
- `test_user` - Sample user data
- `test_admin` - Sample admin data
- `test_access_request` - Sample access request
- `test_policy` - Sample policy
- `mock_jwt_token` - Mock JWT token
- `auth_headers` - Authorization headers

### Mocking Strategy

Tests use mocking to avoid dependencies on external services:

- Firebase Authentication is mocked to avoid real auth calls
- Firestore database is mocked to avoid real database operations
- Policy engine evaluation is mocked for predictable results
- JWT tokens are generated with test secrets

## Test Best Practices

1. **Isolation**: Each test is independent and doesn't rely on other tests
2. **Mocking**: External dependencies are mocked to ensure fast, reliable tests
3. **Assertions**: Tests verify both success and error cases
4. **Coverage**: Tests cover happy paths, edge cases, and error scenarios
5. **Documentation**: Each test has a clear docstring explaining what it tests

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Integration Tests
  run: |
    cd backend
    pip install -r requirements.txt
    pytest tests/ -v --tb=short
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `backend` directory is in Python path
2. **Mock Failures**: Check that mocks are properly configured in conftest.py
3. **Token Errors**: Verify JWT secret matches between test and application
4. **Firestore Errors**: Ensure Firestore mocks are returning expected data structures

### Debug Mode

Run tests with verbose output and full tracebacks:

```bash
pytest tests/ -vv --tb=long
```

### Test Specific Functionality

To test a specific feature in isolation:

```bash
# Test only authentication
pytest tests/test_integration_auth_flow.py -v

# Test with print statements visible
pytest tests/ -v -s
```

## Future Enhancements

- Add performance benchmarking tests
- Implement load testing for rate limiting
- Add security penetration tests
- Expand edge case coverage
- Add visual regression tests for frontend
- Implement contract testing for API endpoints
