# Cognitive Engine API 文档

## 概述

Cognitive Engine API 是一个生产级的 REST API 服务，提供安全的认知引擎接口。

### 特性

- **FastAPI 高性能框架**: 异步支持，自动 OpenAPI 文档
- **JWT 认证与授权**: 多用户层级（FREE/BASIC/PRO/ENTERPRISE）
- **速率限制**: 令牌桶算法，每用户隔离
- **请求验证**: Pydantic 模型验证与 sanitization
- **安全沙箱**: 工业级代码执行沙箱
- **监控系统**: Prometheus 格式指标导出
- **知识图谱**: 安全的图数据库操作

## 快速开始

### 安装依赖

```bash
pip install fastapi uvicorn python-jose[cryptography] python-multipart
```

### 启动服务

```bash
uvicorn src.api.cognitive_api:app --reload --host 0.0.0.0 --port 8000
```

### 访问文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 端点

### 认证端点

#### POST /auth/token

创建访问令牌。

**请求体**:
```json
{
  "username": "string",
  "password": "string",
  "tier": "free"  // 可选：free/basic/pro/enterprise
}
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "tier": "free"
}
```

### 健康检查端点

#### GET /health

返回服务健康状态。

**响应**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### GET /metrics

返回 Prometheus 格式的性能指标。

### 认知查询端点

#### POST /query

处理认知查询请求。

**请求头**:
```
Authorization: Bearer <access_token>
```

**请求体**:
```json
{
  "query": "你的问题或任务描述",
  "context": {},  // 可选上下文
  "use_sandbox": false,  // 是否使用沙箱
  "security_level": "high"  // low/medium/high/paranoid
}
```

**响应**:
```json
{
  "request_id": "req_123456",
  "response": "AI 生成的回答",
  "confidence": 0.95,
  "processing_time_ms": 150,
  "tokens_used": 100
}
```

### 代码执行端点

#### POST /code/execute

在安全沙箱中执行 Python 代码。

**请求体**:
```json
{
  "code": "print('Hello, World!')",
  "timeout": 5,  // 1-30 秒
  "max_memory_mb": 128  // 16-1024 MB
}
```

**响应**:
```json
{
  "request_id": "req_789",
  "output": "Hello, World!\n",
  "exit_code": 0,
  "execution_time_ms": 50,
  "memory_used_mb": 25
}
```

### 知识图谱端点

#### POST /knowledge-graph

操作知识图谱。

**请求体**:
```json
{
  "operation": "add_concept",  // add_concept/query_concept/add_relation/query_relation
  "concept": "Python",
  "properties": {"type": "programming_language"},
  "relations": ["used_for", "has_syntax"]
}
```

## 用户层级与速率限制

| 层级 | 请求/分钟 | 突发容量 | 最大查询长度 |
|------|-----------|----------|-------------|
| FREE | 10 | 15 | 1,000 字符 |
| BASIC | 30 | 50 | 5,000 字符 |
| PRO | 100 | 150 | 10,000 字符 |
| ENTERPRISE | 500 | 750 | 50,000 字符 |

## 安全特性

### JWT 认证

- 使用 HS256 算法签名
- 默认过期时间：60 分钟
- 支持自定义密钥（通过 `COGNITIVE_SECRET_KEY` 环境变量）

### 速率限制

- 基于令牌桶算法
- 每用户独立计数
- 超出限制返回 HTTP 429

### 输入验证

- XSS 防护（检测 `<script`, `javascript:` 等）
- 查询长度限制
- 代码执行沙箱隔离

### CORS 配置

默认允许所有来源（开发环境），生产环境应配置具体域名：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 监控与告警

### Prometheus 指标

访问 `/metrics` 获取以下指标：

- `cognitive_requests_total`: 总请求数
- `cognitive_request_duration_seconds`: 请求耗时
- `cognitive_active_requests`: 活跃请求数
- `cognitive_errors_total`: 错误总数
- `cognitive_rate_limit_hits`: 速率限制触发次数

### 健康检查

定期检查 `/health` 端点以确保服务可用性。

## 错误处理

| HTTP 状态码 | 含义 |
|------------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未认证或 token 过期 |
| 403 | 权限不足 |
| 429 | 速率限制超出 |
| 500 | 服务器内部错误 |

**错误响应格式**:
```json
{
  "detail": "错误描述信息"
}
```

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `COGNITIVE_SECRET_KEY` | JWT 签名密钥 | 随机生成 |
| `COGNITIVE_API_KEY` | LLM API 密钥 | 无（使用 mock） |
| `COGNITIVE_HOST` | 监听地址 | 0.0.0.0 |
| `COGNITIVE_PORT` | 监听端口 | 8000 |
| `COGNITIVE_LOG_LEVEL` | 日志级别 | INFO |

## 示例代码

### Python 客户端

```python
import requests

# 获取 token
response = requests.post("http://localhost:8000/auth/token", json={
    "username": "testuser",
    "password": "testpass",
    "tier": "basic"
})
token = response.json()["access_token"]

# 发送查询
headers = {"Authorization": f"Bearer {token}"}
response = requests.post("http://localhost:8000/query", 
    headers=headers, 
    json={"query": "什么是量子计算？"}
)
print(response.json())
```

### cURL 示例

```bash
# 获取 token
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass","tier":"free"}'

# 发送查询
curl -X POST "http://localhost:8000/query" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"解释相对论"}'
```

## 性能优化建议

1. **启用异步处理**: 使用 `async/await` 处理 I/O 密集型任务
2. **连接池**: 为数据库和外部 API 使用连接池
3. **缓存**: 对频繁查询结果进行缓存（Redis）
4. **负载均衡**: 使用 Nginx 或 HAProxy 进行负载分发
5. **CDN**: 静态资源使用 CDN 加速

## 生产部署清单

- [ ] 配置强密码 JWT 密钥（至少 32 字节）
- [ ] 设置具体的 CORS 白名单
- [ ] 配置 Trusted Hosts 中间件
- [ ] 启用 HTTPS（使用 Let's Encrypt 或其他证书）
- [ ] 配置反向代理（Nginx/Apache）
- [ ] 设置日志轮转
- [ ] 配置监控系统（Prometheus + Grafana）
- [ ] 设置告警规则
- [ ] 进行安全审计和渗透测试
- [ ] 配置自动备份
- [ ] 设置容器化部署（Docker + Kubernetes）

## 故障排除

### 常见问题

**Q: 收到 429 错误怎么办？**
A: 降低请求频率或升级到更高层级。

**Q: Token 过期如何处理？**
A: 重新调用 `/auth/token` 获取新 token。

**Q: 代码执行超时？**
A: 增加 `timeout` 参数或优化代码逻辑。

### 日志查看

```bash
# 查看实时日志
tail -f /var/log/cognitive_api.log

# 搜索错误
grep "ERROR" /var/log/cognitive_api.log
```

## 贡献指南

欢迎提交 Issue 和 Pull Request！请遵循以下流程：

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

## 联系方式

- GitHub Issues: https://github.com/your-org/cognitive-engine/issues
- Email: support@cognitive-engine.com

---

*最后更新：2024 年 7 月*
