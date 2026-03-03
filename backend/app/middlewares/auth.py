from sanic import Request, Sanic
from sanic.response import JSONResponse
from app.utils.jwt import decode_token


def attach_auth_middleware(app: Sanic):
    """附加认证中间件"""
    
    @app.middleware("request")
    async def extract_user(request: Request):
        """从请求中提取用户信息"""
        authorization = request.headers.get("Authorization", "")
        
        if not authorization.startswith("Bearer "):
            request.ctx.user = None
            return
        
        token = authorization.replace("Bearer ", "")
        payload = decode_token(token)
        
        if payload:
            request.ctx.user = {
                "user_id": payload["user_id"],
                "role": payload["role"],
                "permissions": payload.get("permissions", [])
            }
        else:
            request.ctx.user = None


def require_auth_middleware(app: Sanic):
    """要求认证中间件"""
    public_paths = ["/api/v1/auth/login", "/health"]
    
    
    @app.middleware("response")
    async def check_auth(request, response):
        """检查认证"""
        if request.path in public_paths:
            return response
        
        if hasattr(request.ctx, "user") and request.ctx.user is None:
            return JSONResponse(
                {
                    "error": {
                        "code": "UNAUTHORIZED",
                        "message": "未授权访问"
                    }
                },
                status=401
            )
        
        return response
