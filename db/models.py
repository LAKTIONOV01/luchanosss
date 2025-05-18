##############################
# BLOCK WITH DATABASE MODELS #
##############################
from dals import PortalRole
from sqlalchemy import Column, Boolean, String
from sqlalchemy.orm import declarative_base
import uuid
from sqlalchemy.dialects.postgresql import UUID, ARRAY

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean(), default=True)
    hashed_password = Column(String)
    roles = Column(ARRAY(String))

    @property
    def is_superadmin(self) -> bool:
        return PortalRole.ROLE_PORTAL_SUPERADMIN in self.roles

    @property
    def is_admin(self) -> bool:
        return PortalRole.ROLE_PORTAL_ADMIN in self.roles

    @property
    def add_admin_privileges_to_model(self):
        if not self.is_admin:
            return self.roles + [PortalRole.ROLE_PORTAL_ADMIN]

    @property
    def remove_admin_privileges_from_model(self):
        if self.is_admin:
            return [role for role in self.roles if role != PortalRole.ROLE_PORTAL_ADMIN]





