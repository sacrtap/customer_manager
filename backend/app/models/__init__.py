# 导入所有模型以确保它们被 SQLAlchemy 注册
from .user import User
from .role import Role, UserRole
from .permission import Permission
from .customer import Customer
from .operation_log import OperationLog
