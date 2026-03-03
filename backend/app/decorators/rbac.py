from functools import wraps
from sanic import Request
from sanic.response import JSONResponse
from app.utils.rbac import check_rbac


def require_permissions(*permissions):
    """RBAC 权限装饰器"""
    def decorator(f):
        @wraps(f)
        async def wrapper(request: Request, *args, **kwargs):
            if not hasattr(request.ctx, "user") or request.ctx.user is None:
                return JSONResponse(
                    {"error": {"code": "UNAUTHORIZED", "message": "未授权访问"}},
                    status=401
                )
            
            user = request.ctx.user
            user_role = user.get("role", "")
            user_permissions = user.get("permissions", [])
            
            if not check_rbac(user_role, user_permissions, list(permissions)):
                return JSONResponse(
                    {"error": {"code": "FORBIDDEN", "message": "权限不足"}},
                    status=403
                )
            
            return await f(request, *args, **kwargs)
        
        return wrapper
    return decorator
