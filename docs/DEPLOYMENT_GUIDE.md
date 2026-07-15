# 部署指南 v1.0

## 系统要求

- Python 3.10+
- 内存：最低 2GB，推荐 8GB+
- 磁盘：最低 500MB，推荐 5GB+
- 网络：可选（用于 LLM API 访问）

## 快速开始

### 1. 安装依赖

```bash
pip install -e .
```

### 2. 配置环境变量

```bash
export OPENAI_API_KEY="your-api-key"  # 可选，用于 LLM 功能
export LOG_LEVEL="INFO"
export MAX_MEMORY_MB="4096"
```

### 3. 运行 CLI

```bash
python -m src.cli.cognitive_cli
```

### 4. 启动 API 服务（待实现）

```bash
python -m src.api.server --port 8000
```

## 安全配置

### 速率限制

系统默认启用速率限制：
- 默认：60 请求/分钟
- 突发容量：10 请求

修改配置：
```python
from services.rate_limiter import create_rate_limiter, RateLimitStrategy

limiter = create_rate_limiter(
    max_requests=100,
    window_seconds=60.0,
    burst_size=20,
    strategy=RateLimitStrategy.TOKEN_BUCKET
)
```

### 沙箱安全

代码执行沙箱提供以下保护：
- AST 安全检查
- 资源限制（CPU/内存/时间）
- 文件系统隔离
- 网络访问阻断

安全级别：
- `LOW`: 基本隔离
- `MEDIUM`: + AST 检查
- `HIGH`: + 系统调用过滤（默认）
- `PARANOID`: + 完全隔离

## 监控

### 健康检查端点

```bash
curl http://localhost:8000/health
```

返回：
```json
{
  "healthy": true,
  "components": {
    "memory": {"healthy": true, "usage": "45.2%"},
    "disk": {"healthy": true, "usage": "32.1%"}
  }
}
```

### Prometheus 指标

```bash
curl http://localhost:8000/metrics
```

## 性能调优

### 内存优化

```python
from core.config import EngineConfig

config = EngineConfig(
    max_memory_mb=8192,
    gc_threshold=0.7,
)
```

### 并发配置

```python
config = EngineConfig(
    max_workers=4,
    thread_pool_size=8,
)
```

## 故障排除

### 常见问题

1. **内存不足**
   - 降低 `max_memory_mb`
   - 减少并发工作线程

2. **速率限制过严**
   - 调整 `RateLimitConfig`
   - 为不同用户设置不同配额

3. **沙箱执行失败**
   - 检查代码是否包含禁止的 AST 节点
   - 提高超时时间或内存限制

### 日志查看

```bash
# CLI 模式
cog-engine logs INFO

# 直接查看日志文件
tail -f logs/engine.log
```

## 生产部署建议

1. **使用 Docker 容器化**
   ```bash
   docker build -t cognitive-engine .
   docker run -p 8000:8000 cognitive-engine
   ```

2. **配置反向代理**
   - 使用 Nginx 或 Traefik
   - 启用 HTTPS
   - 配置负载均衡

3. **设置告警**
   - CPU 使用率 > 80%
   - 内存使用率 > 90%
   - 错误率 > 1%

4. **定期备份**
   - 知识图谱数据
   - 配置文件
   - 日志归档

## 升级指南

### 从 v0.x 升级到 v1.0

1. 备份现有配置和数据
2. 更新依赖：`pip install --upgrade ai-cognition-engine`
3. 迁移配置（如有需要）
4. 重启服务

## 联系支持

- GitHub Issues: https://github.com/your-org/cognitive-engine/issues
- 文档：https://docs.cognitive-engine.ai
