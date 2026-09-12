from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from prometheus.auth.jwt import decode_access_token
from prometheus.auth.models import User, UserRole
from prometheus.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = decode_access_token(token)
    if token_data is None:
        raise credentials_exception
    
    # Normally we would fetch the user from the database here
    # For now, we mock returning a User object from the decoded token
    user = User(
        id=token_data.email or "unknown",
        email=token_data.email or "unknown@example.com",
        role=token_data.role or UserRole.VIEWER
    )
    return user

def require_role(allowed_roles: List[UserRole]):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted"
            )
        return current_user
    return role_checker

def verify_api_key(api_key: Optional[str] = Depends(api_key_header)) -> bool:
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key is missing",
        )
    # Normally we would check the API key against the database.
    # For demonstration, we assume valid if it matches a dummy secret or check DB.
    # We will use a mock check:
    if api_key != "secret-api-key": # TODO: Replace with DB validation
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key",
        )
    return True

def get_institutional_consumer(api_key_valid: bool = Depends(verify_api_key)) -> User:
    """Returns a dummy user representing the institutional API consumer."""
    return User(
        id="institution-1",
        email="institution@example.com",
        role=UserRole.INSTITUTIONAL_API
    )
