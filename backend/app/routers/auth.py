from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import create_access_token, current_user, verify_password
from ..database import get_db
from ..models import User
from ..schemas import LoginRequest, TokenResponse, UserOut

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Annotated[Session, Depends(get_db)]) -> TokenResponse:
    user = db.scalar(select(User).where(User.username == data.username))
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    if user.role != data.role:
        raise HTTPException(status_code=403, detail="This account is not authorized for the selected role")
    return TokenResponse(access_token=create_access_token(user))


@router.get("/me", response_model=UserOut)
def me(user: Annotated[User, Depends(current_user)]) -> User:
    return user
