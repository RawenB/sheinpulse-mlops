from fastapi import APIRouter, Depends, HTTPException, status

from app.auth_schemas import LoginRequest, TokenResponse, AdminInfo
from app.security import verify_admin_credentials, create_access_token
from app.dependencies import get_current_admin

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest):
    if not verify_admin_credentials(data.email, data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        {
            "sub": data.email,
            "role": "admin",
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=AdminInfo)
def get_me(current_admin: dict = Depends(get_current_admin)):
    return current_admin