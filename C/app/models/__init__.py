# Import all models to ensure they are registered with SQLAlchemy
from app.models.jwxt import JWXTBinding, JWXTUserInfo
from app.models.profile import UserProfile
from app.models.test_record import UserTestRecord
from app.models.user import User, UserRole

__all__ = ["User", "UserRole", "UserProfile", "UserTestRecord", "JWXTBinding", "JWXTUserInfo"]
