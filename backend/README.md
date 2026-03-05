# 客户运营中台 - 后端

基于 Sanic 框架的客户信息管理后端服务。

## 技术栈

- Python 3.11
- Sanic 23.6.0
- SQLAlchemy 2.0 (异步)
- PostgreSQL
- JWT 认证
- Pydantic 验证

## 开发

```bash
pip install -r requirements.txt
python -m sanic main.app --host 0.0.0.0 --port 8000 --reload
```

## 测试

```bash
pytest -v
```
