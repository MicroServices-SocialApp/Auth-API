from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
import httpx
import os

router = APIRouter(tags=["login"])


# --- CONFIGURATION ---
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
# ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# --- UTILS ---
def create_access_token(data, expires_delta: Optional[timedelta] = None) -> str:
    if not SECRET_KEY:
        raise ValueError("CRITICAL: SECRET_KEY environment variable is required.")
    if not ALGORITHM:
        raise ValueError("CRITICAL: ALGORITHM environment variable is required.")
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# --- LOGIN ENDPOINT ---
@router.post(
    "/login",
    deprecated=False,
    name='login',
    summary="Create a token for a user.",
    description="",
    response_model=None,
    status_code=status.HTTP_200_OK,
    response_description="User token is issued",
    responses={
        200: {
            "description": "SUCCESS - The token was created!",
        }
    }
)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    1. Receive username/password.
    2. Call User Service to get the stored user (and hash).
    3. Verify password.
    4. Issue Token.
    """

    
    async with httpx.AsyncClient() as client:
        try:
            if not SECRET_KEY:
                raise ValueError("CRITICAL: SECRET_KEY environment variable is required.")
            
            # We use the service name 'user-api' which Docker resolves automatically
            response = await client.get(
                "http://user-api/user/read_user_by_username",    #"http://user-api:8000/user/read_user_by_username" when not using kubernetes
                params={"username": form_data.username},
                headers={"x-internal-token": SECRET_KEY}
            )
            # This will jump straight to the 'except httpx.HTTPStatusError' block if status is not 2xx
            response.raise_for_status()

        except httpx.RequestError as e:
            # Happens if the service is totally down or DNS fails
            raise HTTPException(
                status_code=503, 
                detail=f"User Service unreachable: {e}"
            )

        except httpx.HTTPStatusError as e:
            # Happens if service replied with 401, 404, 500, etc.
            if e.response.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Incorrect username or password: {e}",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            # Fallback for other status errors (like 404 or 500)
            raise HTTPException(
                status_code=e.response.status_code, 
                detail=f"500 error: {e}"
            )

    user_data = response.json()

    
    if not check_password_hash(user_data["hashed_password"], form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user_data["id"])})

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
