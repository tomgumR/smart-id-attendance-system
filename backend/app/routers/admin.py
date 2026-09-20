from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import hash_password, require_roles
from ..database import get_db
from ..models import Role, User
from ..schemas import UserCreate, UserOut

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/users", response_model=UserOut, status_code=201)
def create_user(data: UserCreate, db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(require_roles(Role.ADMIN))]) -> User:
    if db.scalar(select(User).where(User.username == data.username)):
        raise HTTPException(status_code=409, detail="Username already exists")
    user = User(username=data.username, password_hash=hash_password(data.password), role=data.role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/users", response_model=list[UserOut])
def list_users(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(require_roles(Role.ADMIN))]) -> list[User]:
    return list(db.scalars(select(User).order_by(User.username)))
