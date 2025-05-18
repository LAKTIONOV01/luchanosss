from db.models import User
from db.dals import PortalRole
from fastapi import HTTPException


def check_user_permissions(target_user: User, current_user: User) -> bool:
    if PortalRole.ROLE_PORTAL_SUPERADMIN in current_user.roles:
        raise HTTPException(
            status_code=406, detail='Superadmin cannot be deleted via API.'
        )
    if target_user.user_id != current_user.user_id:
        if not {
            PortalRole.ROLE_PORTAL_ADMIN,
            PortalRole.ROLE_PORTAL_SUPERADMIN,
        }.intersection(current_user.roles):
            return False

        if (PortalRole.ROLE_PORTAL_SUPERADMIN in target_user.roles
                and PortalRole.ROLE_PORTAL_ADMIN in current_user.roles
        ):
            return False

        if PortalRole.ROLE_PORTAL_ADMIN in target_user.roles and PortalRole.ROLE_PORTAL_ADMIN in current_user.roles:
            return False
    return True
