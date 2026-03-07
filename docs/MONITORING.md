# 监控与日志配置

## 日志配置

### 后端日志 (Sanic)

后端日志已配置在 `app/config.py` 中，支持以下级别：

- **DEBUG**: 调试信息（开发环境）
- **INFO**: 运行信息（生产环境）
- **WARNING**: 警告信息
- **ERROR**: 错误信息

日志输出位置：
- **开发环境**: 控制台
- **生产环境**: Docker 日志 + 可选的文件日志

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看后端日志
docker-compose logs -f backend

# 查看前端日志
docker-compose logs -f frontend

# 查看数据库日志
docker-compose logs -f postgres

# 查看最近 100 行
docker-compose logs --tail=100 backend
```

## 健康检查端点

### 后端健康检查

```bash
# 简单健康检查
curl http://localhost:8000/api/v1/health

# 详细健康检查 (包含数据库连接)
curl http://localhost:8000/api/v1/health?detailed=true
```

响应示例：
```json
{
  "status": "healthy",
  "timestamp": "2026-03-07T12:00:00Z",
  "version": "1.0.0",
  "database": "connected",
  "services": {
    "database": "up",
    "cache": "up"
  }
}
```

## Docker Compose 健康检查

`docker-compose.yml` 已配置健康检查：

```yaml
services:
  backend:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
  
  postgres:
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U customer_manager -d customer_manager"]
      interval: 10s
      timeout: 5s
      retries: 5
```

## 监控指标

### 关键指标

1. **API 响应时间**: 应在 200ms 以内
2. **数据库连接数**: 监控连接池使用情况
3. **错误率**: 应低于 1%
4. **内存使用**: 后端容器内存使用率

### 使用 Docker Stats 监控

```bash
# 实时查看资源使用
docker stats

# 查看所有容器统计
docker stats --no-stream
```

## 告警配置 (可选)

### 使用 Prometheus + Grafana

如需更高级的监控，可以添加 Prometheus 和 Grafana：

1. 在 `docker-compose.yml` 中添加监控服务
2. 配置 Prometheus 抓取后端指标
3. 使用 Grafana 仪表盘可视化

### 日志聚合 (可选)

使用 ELK Stack (Elasticsearch, Logstash, Kibana) 或 Loki + Grafana:

```yaml
# docker-compose.monitoring.yml
services:
  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
  
  promtail:
    image: grafana/promtail:latest
    volumes:
      - /var/log:/var/log
  
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
```

## 性能优化建议

1. **启用 Gzip 压缩**: Nginx 已配置
2. **启用缓存**: 静态资源缓存 1 年
3. **数据库连接池**: 已优化配置
4. **异步处理**: 使用异步 SQLAlchemy

## 故障排查

### 后端无法启动

```bash
# 查看后端日志
docker-compose logs backend

# 检查数据库连接
docker-compose exec backend python -c "from app.config import settings; print(settings.database_url)"

# 检查端口占用
lsof -i :8000
```

### 数据库连接失败

```bash
# 检查数据库是否运行
docker-compose ps postgres

# 查看数据库日志
docker-compose logs postgres

# 测试数据库连接
docker-compose exec postgres psql -U customer_manager -d customer_manager
```

### 前端无法访问

```bash
# 检查前端容器状态
docker-compose ps frontend

# 查看前端日志
docker-compose logs frontend

# 检查 Nginx 配置
docker-compose exec nginx nginx -t
```
