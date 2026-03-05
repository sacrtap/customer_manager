from sanic import Request, Sanic
from sanic.response import JSONResponse

from app.utils.jwt import decode_token


def attach_auth_middleware(app: Sanic):
    """附加认证中间件"""

    @app.middleware("request")
    async def extract_user(request: Request):
        """从请求中提取用户信息"""
        if not hasattr(request.ctx, "user"):
            request.ctx.user = None

        authorization = request.headers.get("Authorization", "")

        if not authorization.startswith("Bearer "):
            return

        token = authorization[7:]
        payload = decode_token(token)

        if payload:
            request.ctx.user = {
                "user_id": payload["user_id"],
                "role": payload["role"],
                "permissions": payload.get("permissions", []),
            }


def require_auth_middleware(app: Sanic):
    """要求认证中间件"""
    public_paths = ["/api/v1/auth/login", "/health", "/public"]

    @app.middleware("response")
    async def check_auth(request, response):
        """检查认证"""
        if request.path in public_paths:
            return response

        if not hasattr(request.ctx, "user") or request.ctx.user is None:
            return JSONResponse(
                {"error": {"code": "UNAUTHORIZED", "message": "未授权访问"}}, status=401
            )

        return response
