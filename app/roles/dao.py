from app.dao.base import BaseDAO
from app.roles.models import Role

class RolesDAO(BaseDAO):
    model = Role