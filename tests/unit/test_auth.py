import pytest
from datetime import timedelta
from fastapi import HTTPException
from prometheus.auth.models import UserRole
from prometheus.auth.jwt import create_access_token, decode_access_token, get_password_hash, verify_password
from prometheus.auth.rbac import get_current_user, require_role, verify_api_key

def test_password_hashing():
    password = "secretpassword123"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False

def test_create_and_decode_token():
    data = {"sub": "admin@example.com", "role": UserRole.ADMIN.value}
    token = create_access_token(data, expires_delta=timedelta(minutes=5))
    
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded.email == "admin@example.com"
    assert decoded.role == UserRole.ADMIN

def test_decode_invalid_token():
    assert decode_access_token("invalid.token.string") is None

def test_get_current_user_valid():
    data = {"sub": "analyst@example.com", "role": UserRole.ANALYST.value}
    token = create_access_token(data)
    user = get_current_user(token)
    assert user.email == "analyst@example.com"
    assert user.role == UserRole.ANALYST

def test_get_current_user_invalid():
    with pytest.raises(HTTPException) as excinfo:
        get_current_user("invalid_token")
    assert excinfo.value.status_code == 401

def test_require_role():
    data = {"sub": "viewer@example.com", "role": UserRole.VIEWER.value}
    token = create_access_token(data)
    user = get_current_user(token)
    
    checker = require_role([UserRole.VIEWER, UserRole.ADMIN])
    # Should pass without exception
    returned_user = checker(current_user=user)
    assert returned_user.email == user.email
    
    checker_fail = require_role([UserRole.ADMIN])
    with pytest.raises(HTTPException) as excinfo:
        checker_fail(current_user=user)
    assert excinfo.value.status_code == 403

def test_verify_api_key():
    assert verify_api_key("secret-api-key") is True
    
    with pytest.raises(HTTPException) as excinfo:
        verify_api_key(None)
    assert excinfo.value.status_code == 401
    
    with pytest.raises(HTTPException) as excinfo:
        verify_api_key("wrong-api-key")
    assert excinfo.value.status_code == 403
