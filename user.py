from db.models import User
from db.dals import PortalRole


def check_user_permissions(target_user: User, current_user: User) -> bool:
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
    return True
