from sqlalchemy.orm import Session
from ..database import models
from ..core import security

class AuthService:
    @staticmethod
    def authenticate_user(db: Session, email: str, dni: str):
        user = db.query(models.Docente).filter(models.Docente.email == email).first()
        if not user:
            return None
        if not security.verify_password(dni, user.dni):
            return None
        return user
