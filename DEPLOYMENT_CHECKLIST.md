# 部署检查清单 (Deployment Checklist)

## 部署前检查

### 环境准备
- [ ] Docker 20.10+ 已安装
- [ ] Docker Compose 2.0+ 已安装
- [ ] Git 已安装
- [ ] PostgreSQL 客户端工具已安装 (可选)

### 配置文件
- [ ] `.env` 文件已创建并配置
- [ ] `backend/.env` 文件已创建
- [ ] JWT_SECRET 已修改为随机密钥
- [ ] DB_PASSWORD 已修改为强密码
- [ ] ENVIRONMENT 设置为 `production`

### 安全检查
- [ ] 默认管理员密码已修改
- [ ] 数据库密码复杂度符合要求
- [ ] JWT_SECRET 长度 >= 32 字符
- [ ] .gitignore 已包含敏感文件

## 部署步骤

### 1. 本地验证
```bash
# 验证 Docker Compose 配置
docker-compose config

# 检查语法错误
docker-compose -f docker-compose.yml config --quiet
```

### 2. 启动服务
```bash
# 一键部署脚本
./deploy.sh

# 或手动启动
docker-compose up -d
```

### 3. 数据库初始化
```bash
docker-compose exec backend python init_db.py
docker-compose exec backend python init_role_permissions.py
```

### 4. 健康检查
```bash
# 检查服务状态
docker-compose ps

# 检查后端健康
curl http://localhost:8000/api/v1/health

# 检查前端
curl http://localhost:3000
```

### 5. 功能验证
- [ ] 登录页面可访问
- [ ] 管理员可以登录
- [ ] Dashboard 数据正常显示
- [ ] 客户列表可加载
- [ ] API 端点响应正常

## 性能检查

### 数据库
- [ ] 连接池配置正确 (pool_size=10, max_overflow=20)
- [ ] 慢查询日志已启用
- [ ] 索引已创建 (created_at, status, sales_owner_id)

### 后端
- [ ] Worker 数量 >= CPU 核心数
- [ ] 日志级别设置为 INFO 或 WARNING
- [ ] 请求超时配置合理

### 前端
- [ ] 静态资源已压缩
- [ ] Gzip 压缩已启用
- [ ] 缓存策略已配置

## 监控告警

### 日志
- [ ] 应用日志正常输出
- [ ] 错误日志可查询
- [ ] 日志轮转已配置

### 监控
- [ ] 健康检查端点可访问
- [ ] 关键指标已监控 (CPU, 内存，磁盘)
- [ ] 告警规则已配置

## 备份恢复

### 数据库备份
- [ ] 定期备份任务已配置
- [ ] 备份文件存储安全
- [ ] 恢复流程已验证

### 应急预案
- [ ] 服务回滚流程已文档化
- [ ] 紧急联系人列表已更新
- [ ] 故障排查手册已准备

## 文档更新

- [ ] README.md 已更新
- [ ] API 文档已生成
- [ ] 用户手册已准备
- [ ] 运维手册已文档化

## 上线确认

- [ ] 所有测试通过
- [ ] 性能指标达标
- [ ] 安全扫描通过
- [ ] 相关干系人已通知
- [ ] 上线时间窗口已确认

---

## 快速回滚

如果部署失败，执行回滚：

```bash
# 停止新服务
docker-compose down

# 恢复数据库备份
docker-compose exec -T postgres psql -U customer_manager customer_manager < backup.sql

# 启动旧版本
git checkout <previous-tag>
docker-compose up -d
```

---

## 联系支持

- 技术支持：tech@example.com
- 运维支持：ops@example.com
- 紧急联系：+86-xxx-xxxx-xxxx
