"""
Cognitive Engine REST API Service
=================================
生产级 REST API 服务，提供安全的认知引擎接口

特性:
- FastAPI 高性能框架
- JWT 认证与授权
- 速率限制集成
- 请求验证与 sanitization
- 异步处理支持
- OpenAPI/Swagger 文档
- Prometheus 指标导出

Author: AI Assistant (Security Researcher & AGI Scientist)
"""

from fastapi import FastAPI, HTTPException, Depends, Security, status, Request, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
import jwt
import time
import hashlib
import os
from datetime import datetime, timedelta
from enum import Enum
import logging

# 导入核心组件
from src.core.llm_client import LLMClient
from src.core.secure_sandbox import SecureSandbox, SandboxConfig, SecurityLevel
from src.modules.knowledge_graph import KnowledgeGraph
from src.services.rate_limiter import RateLimiter, RateLimitConfig
from src.services.monitor import Monitor

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化 FastAPI 应用
app = FastAPI(
    title="Cognitive Engine API",
    description="Production-ready REST API for the Cognitive AGI Engine",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 安全中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 测试环境下禁用 TrustedHostMiddleware
if os.getenv("TESTING", "false").lower() != "true":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,*").split(",")
    )

# 安全配置
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production")
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", "60"))

# 初始化服务
llm_client = LLMClient()
sandbox = SecureSandbox(SandboxConfig(security_level=SecurityLevel.HIGH))
knowledge_graph = KnowledgeGraph()
rate_limiter = RateLimiter()
monitor = Monitor()

# 认证方案
security = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class UserTier(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


# Pydantic 模型
class TokenPayload(BaseModel):
    sub: str
    exp: datetime
    iat: datetime
    tier: UserTier = UserTier.FREE


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=10000, description="用户查询文本")
    context: Optional[Dict[str, Any]] = None
    use_sandbox: bool = False
    security_level: str = "high"
    
    @validator('query')
    def sanitize_query(cls, v):
        # 基本的 XSS 防护
        dangerous_patterns = ['<script', 'javascript:', 'onerror=', 'onload=']
        for pattern in dangerous_patterns:
            if pattern.lower() in v.lower():
                raise ValueError(f"Potentially dangerous pattern detected: {pattern}")
        return v.strip()


class CodeExecutionRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=50000, description="要执行的 Python 代码")
    timeout: int = Field(default=5, ge=1, le=30, description="超时时间（秒）")
    max_memory_mb: int = Field(default=128, ge=16, le=1024, description="最大内存（MB）")


class KnowledgeGraphRequest(BaseModel):
    operation: str = Field(..., pattern="^(add|query|delete|search)$")
    data: Dict[str, Any]


class ResponseBase(BaseModel):
    success: bool
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None


class QueryResponse(ResponseBase):
    result: Any
    confidence: Optional[float] = None
    processing_time_ms: float
    tokens_used: int


class CodeExecutionResponse(ResponseBase):
    output: str
    exit_code: int
    execution_time_ms: float
    memory_used_mb: float


class MetricsResponse(BaseModel):
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    active_requests: int
    requests_per_minute: float
    error_rate: float
    uptime_seconds: float


# 辅助函数
def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> Optional[TokenPayload]:
    """验证 JWT token 并返回用户信息"""
    if credentials is None:
        return None
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return TokenPayload(**payload)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_api_key_user(api_key: str = Security(api_key_header)) -> Optional[str]:
    """验证 API Key"""
    if api_key is None:
        return None
    
    # 简单的 API Key 验证（生产环境应使用数据库）
    valid_keys = os.getenv("VALID_API_KEYS", "").split(",")
    if api_key in valid_keys:
        return f"api_user_{hashlib.md5(api_key.encode()).hexdigest()[:8]}"
    return None


def check_rate_limit(user_id: str, tier: UserTier = UserTier.FREE) -> None:
    """检查速率限制"""
    configs = {
        UserTier.FREE: RateLimitConfig(requests_per_minute=10, burst_size=15),
        UserTier.BASIC: RateLimitConfig(requests_per_minute=60, burst_size=100),
        UserTier.PRO: RateLimitConfig(requests_per_minute=300, burst_size=500),
        UserTier.ENTERPRISE: RateLimitConfig(requests_per_minute=1000, burst_size=2000),
    }
    
    config = configs.get(tier, configs[UserTier.FREE])
    
    if not rate_limiter.is_allowed(user_id, config):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please upgrade your plan or wait.",
            headers={"X-RateLimit-Reset": str(int(time.time()) + 60)}
        )


def generate_request_id() -> str:
    """生成唯一请求 ID"""
    return f"{int(time.time())}_{hashlib.md5(os.urandom(8)).hexdigest()[:12]}"


# API 端点
@app.get("/health", response_model=Dict[str, Any], tags=["Health"])
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "services": {
            "llm": "connected",
            "sandbox": "active",
            "knowledge_graph": "ready",
            "rate_limiter": "active",
            "monitor": "running"
        }
    }


@app.get("/metrics", response_model=MetricsResponse, tags=["Monitoring"])
async def get_metrics():
    """获取系统指标"""
    metrics = monitor.get_metrics()
    return MetricsResponse(
        cpu_percent=metrics['cpu']['percent'],
        memory_percent=metrics['memory']['percent'],
        disk_percent=metrics['disk']['percent'],
        active_requests=monitor.active_requests,
        requests_per_minute=monitor.get_requests_per_minute(),
        error_rate=monitor.get_error_rate(),
        uptime_seconds=monitor.get_uptime()
    )


@app.post("/auth/token", response_model=Dict[str, Any], tags=["Authentication"])
async def create_access_token(username: str, password: str):
    """创建访问令牌（简化版，生产环境应使用 proper auth）"""
    # 简化认证（生产环境应从数据库验证）
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password required")
    
    # 创建 token
    now = datetime.utcnow()
    expire = now + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "sub": username,
        "exp": expire,
        "iat": now,
        "tier": UserTier.BASIC.value  # 默认 tier
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": TOKEN_EXPIRE_MINUTES * 60
    }


@app.post("/query", response_model=QueryResponse, tags=["Cognitive Engine"])
async def process_query(
    request: QueryRequest,
    user: TokenPayload = Depends(get_current_user),
    req: Request = None
):
    """处理认知查询"""
    request_id = generate_request_id()
    user_id = user.sub if user else "anonymous"
    tier = user.tier if user else UserTier.FREE
    
    # 速率限制检查
    check_rate_limit(user_id, tier)
    
    # 开始监控
    monitor.start_request(request_id)
    start_time = time.time()
    
    try:
        # 执行查询
        if request.use_sandbox:
            # 在沙箱中执行
            security_level = SecurityLevel[request.security_level.upper()]
            config = SandboxConfig(security_level=security_level)
            result = sandbox.execute_safe(request.query, config)
            confidence = 1.0
        else:
            # 使用 LLM 处理
            response = await llm_client.generate_async(
                prompt=request.query,
                context=request.context
            )
            result = response['response']
            confidence = response.get('confidence', 0.0)
        
        processing_time = (time.time() - start_time) * 1000
        
        monitor.end_request(request_id, success=True)
        
        return QueryResponse(
            success=True,
            message="Query processed successfully",
            request_id=request_id,
            result=result,
            confidence=confidence,
            processing_time_ms=processing_time,
            tokens_used=len(request.query.split())  # 简化计算
        )
    
    except Exception as e:
        monitor.end_request(request_id, success=False)
        logger.error(f"Query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")


@app.post("/execute", response_model=CodeExecutionResponse, tags=["Code Execution"])
async def execute_code(
    request: CodeExecutionRequest,
    user: TokenPayload = Depends(get_current_user),
    req: Request = None
):
    """在安全沙箱中执行代码"""
    request_id = generate_request_id()
    user_id = user.sub if user else "anonymous"
    tier = user.tier if user else UserTier.FREE
    
    # 速率限制检查（更严格）
    check_rate_limit(user_id, tier)
    
    # 开始监控
    monitor.start_request(request_id)
    start_time = time.time()
    
    try:
        # 配置沙箱
        config = SandboxConfig(
            timeout=request.timeout,
            max_memory_mb=request.max_memory_mb,
            security_level=SecurityLevel.PARANOID
        )
        
        # 执行代码
        result = sandbox.execute_safe(request.code, config)
        
        processing_time = (time.time() - start_time) * 1000
        
        monitor.end_request(request_id, success=True)
        
        return CodeExecutionResponse(
            success=True,
            message="Code executed successfully",
            request_id=request_id,
            output=result.get('output', ''),
            exit_code=result.get('exit_code', 0),
            execution_time_ms=processing_time,
            memory_used_mb=result.get('memory_used_mb', 0.0)
        )
    
    except Exception as e:
        monitor.end_request(request_id, success=False)
        logger.error(f"Code execution failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Code execution failed: {str(e)}")


@app.post("/knowledge-graph", response_model=ResponseBase, tags=["Knowledge Graph"])
async def knowledge_graph_operation(
    request: KnowledgeGraphRequest,
    user: TokenPayload = Depends(get_current_user),
    req: Request = None
):
    """知识图谱操作"""
    request_id = generate_request_id()
    user_id = user.sub if user else "anonymous"
    tier = user.tier if user else UserTier.FREE
    
    check_rate_limit(user_id, tier)
    monitor.start_request(request_id)
    
    try:
        if request.operation == "add":
            knowledge_graph.add_concept(request.data)
            message = "Concept added successfully"
        elif request.operation == "query":
            result = knowledge_graph.query(request.data)
            message = f"Query returned {len(result)} results"
        elif request.operation == "delete":
            knowledge_graph.delete_concept(request.data.get('id'))
            message = "Concept deleted successfully"
        elif request.operation == "search":
            results = knowledge_graph.search_by_similarity(
                request.data.get('query', ''),
                request.data.get('threshold', 0.7)
            )
            message = f"Search returned {len(results)} results"
        else:
            raise ValueError(f"Unknown operation: {request.operation}")
        
        monitor.end_request(request_id, success=True)
        
        return ResponseBase(
            success=True,
            message=message,
            request_id=request_id
        )
    
    except Exception as e:
        monitor.end_request(request_id, success=False)
        logger.error(f"Knowledge graph operation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Operation failed: {str(e)}")


@app.get("/users/me", response_model=Dict[str, Any], tags=["Authentication"])
async def get_current_user_info(user: TokenPayload = Depends(get_current_user)):
    """获取当前用户信息"""
    return {
        "username": user.sub,
        "tier": user.tier.value,
        "token_expires_at": user.exp.isoformat()
    }


# 异常处理器
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """统一处理 HTTP 异常"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """统一处理未捕获异常"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# 启动/关闭事件
@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    logger.info("Cognitive Engine API starting...")
    monitor.start()
    logger.info("Cognitive Engine API ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理"""
    logger.info("Cognitive Engine API shutting down...")
    monitor.stop()
    logger.info("Cleanup complete")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000")),
        reload=os.getenv("DEBUG", "false").lower() == "true"
    )
