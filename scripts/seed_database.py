"""Create development-only accounts. Run from backend: python ../scripts/seed_database.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from sqlalchemy import select
from app.auth import hash_password
from app.database import Base, SessionLocal, engine
from app.models import Role, User

ACCOUNTS = [("admin", "admin123", Role.ADMIN), ("guard1", "guard123", Role.SECURITY), ("professor1", "professor123", Role.PROFESSOR)]


def main() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        for username, password, role in ACCOUNTS:
            user = db.scalar(select(User).where(User.username == username))
            if user:
                user.password_hash, user.role = hash_password(password), role
            else:
                db.add(User(username=username, password_hash=hash_password(password), role=role))
        db.commit()
    print("Development accounts created/updated. Change these passwords outside a demo.")


if __name__ == "__main__":
    main()
