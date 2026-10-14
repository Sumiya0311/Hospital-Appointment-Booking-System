from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.models.user import User
from app.models.patient import Patient
from app.models.refresh_token import RefreshToken
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.schemas.user import AdminCreateUser, UserResponse
from app.auth.password import hash_password, verify_password
from app.auth.jwt import create_access_token, create_refresh_token
from app.auth.dependencies import require_admin

router = APIRouter(prefix="/auth", tags=["Authentication"])


class RefreshRequest(BaseModel):
    refresh_token: str


@router.get("/test")
def test_auth():
    return {"message": "Authentication router is working"}


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_patient(
    data: RegisterRequest,
    db: Session = Depends(get_db),
):
    try:
        existing_user = db.query(User).filter(
            User.email == data.email
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email is already registered",
            )

        user = User(
            name=data.name,
            email=data.email,
            phone=data.phone,
            hashed_password=hash_password(data.password),
            role="Patient",
            is_active=True,
        )

        db.add(user)
        db.flush()

        patient = Patient(
            user_id=user.id,
            name=data.name,
            phone=data.phone,
            is_active=True,
        )

        db.add(patient)
        db.commit()
        db.refresh(user)

        return {
            "message": "Patient registered successfully",
            "user_id": user.id,
            "name": user.name,
            "email": user.email,
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Patient registration failed",
        )


@router.post("/login", response_model=TokenResponse)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(
        User.email == data.email
    ).first()

    if not user or not verify_password(
        data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is inactive",
        )

    access_token = create_access_token({
        "sub": str(user.id),
        "role": user.role,
    })

    refresh_token = create_refresh_token({
        "sub": str(user.id),
        "role": user.role,
    })

    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    try:
        db.add(
            RefreshToken(
                user_id=user.id,
                token=refresh_token,
                is_revoked=False,
                expires_at=expires_at,
            )
        )
        db.commit()

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save refresh token",
        )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_tokens(
    data: RefreshRequest,
    db: Session = Depends(get_db),
):
    try:
        payload = jwt.decode(
            data.refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        user_id = int(payload["sub"])

    except HTTPException:
        raise

    except (JWTError, ValueError, KeyError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    stored = db.query(RefreshToken).filter(
        RefreshToken.token == data.refresh_token,
        RefreshToken.user_id == user_id,
        RefreshToken.is_revoked.is_(False),
    ).first()

    if not stored:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is revoked or not registered",
        )

    expiry = stored.expires_at
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)

    if expiry <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive or missing",
        )

    new_access_token = create_access_token({
        "sub": str(user.id),
        "role": user.role,
    })

    new_refresh_token = create_refresh_token({
        "sub": str(user.id),
        "role": user.role,
    })

    new_expiry = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    try:
        stored.is_revoked = True

        db.add(
            RefreshToken(
                user_id=user.id,
                token=new_refresh_token,
                is_revoked=False,
                expires_at=new_expiry,
            )
        )

        db.commit()

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not rotate refresh token",
        )

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
    )


@router.post("/logout")
def logout(
    data: RefreshRequest,
    db: Session = Depends(get_db),
):
    stored = db.query(RefreshToken).filter(
        RefreshToken.token == data.refresh_token,
        RefreshToken.is_revoked.is_(False),
    ).first()

    if not stored:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked token",
        )

    stored.is_revoked = True
    db.commit()

    return {"message": "Logged out successfully"}


@router.post(
    "/admin/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_admin_user(
    data: AdminCreateUser,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    existing_user = db.query(User).filter(
        User.email == data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    user = User(
        name=data.name,
        email=data.email,
        phone=data.phone,
        hashed_password=hash_password(data.password),
        role=data.role,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user