# 导入所有模型以确保它们被 SQLAlchemy 注册
from .customer import Customer
from .operation_log import OperationLog
from .permission import Permission
from .role import Role, UserRole
from .user import User
from .billing import Billing
