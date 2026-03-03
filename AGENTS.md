# AGENTS.md

This file contains guidelines for agentic coding assistants working in this repository.

## 交互要求
- Thinking 思考过程用中文表述.
- Reply 回答也要用中文回复.
- 所有生成的文档都要使用中文，且符合中文的语法规范.
- Use context7 for all code generation and API documentation questions.
- 针对所有错误后修复成功的经验进行总结，把必要的经验写更新至AGENTS.md中，以避免再犯错.

## Project Status

This is a new customer_manager project. The codebase is currently being initialized.

## Build, Lint, and Test Commands

### Build
```bash
# Detect build system and provide appropriate command
# Examples (to be determined based on tech stack):
# npm run build
# python -m build
# cargo build
# make build
```

### Linting
```bash
# Run linter (to be determined based on tech stack):
# npm run lint
# ruff check
# cargo clippy
# make lint
```

### Formatting
```bash
# Format code (to be determined based on tech stack):
# npm run format
# black .
# cargo fmt
# make format
```

### Testing
```bash
# Run all tests (to be determined based on tech stack):
# npm test
# pytest
# cargo test
# make test
```

### Run Single Test
```bash
# Run specific test file (examples based on tech stack):
# npm test -- path/to/test.test.js
# pytest path/to/test.py
# cargo test test_name
```

## Code Style Guidelines

### General Principles
- Write clear, self-documenting code
- Keep functions small and focused on a single responsibility
- Follow existing patterns in the codebase
- Add comments only when necessary to explain complex logic

### Import Ordering
- Group imports: standard library → third-party → local modules
- Sort alphabetically within each group
- Separate groups with blank lines

### Formatting
- Use standard formatting for the chosen language
- Maximum line length: 100 characters (or language standard)
- Use meaningful indentation

### Type System
- Use type hints/annotations for all function parameters and return values
- Avoid `any` types; use specific types or interfaces
- Prefer strict type checking

### Naming Conventions
- **Variables/Functions**: `camelCase` (JavaScript/TypeScript) or `snake_case` (Python/Rust)
- **Classes/Types**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **File names**: `kebab-case` or `snake_case` depending on language conventions
- Use descriptive, meaningful names that explain purpose

### Error Handling
- Never silently swallow errors
- Use appropriate error types for the language
- Provide context in error messages (what happened and why)
- Handle errors at appropriate abstraction levels
- Log errors with sufficient context for debugging

### Function Design
- Default to pure functions when possible
- Limit function parameters to 3-5 (use objects for many parameters)
- Return early for guard clauses
- Use explicit returns rather than implicit ones

### Comments
- Write code that is self-explanatory
- Only comment "why", not "what"
- Keep comments up-to-date with code changes
- Use TODO/FIXME comments sparingly with context

### Testing Guidelines
- Write tests for all public APIs
- Aim for high test coverage on critical paths
- Use descriptive test names that explain what is being tested
- Arrange tests in Given-When-Then structure when appropriate
- Mock external dependencies
- Test edge cases and error conditions

### Testing Development Rules (测试开发规则)
**重要**：以下规则基于实际开发中的问题总结，必须严格遵守以避免重复错误。

1. **Git Worktree规则**
   - 使用git worktree时，所有文件操作（读取、写入、编辑）必须使用workdir参数指定正确的工作树目录
   - 否则文件会被创建在错误的目录（主目录而非工作树目录）

2. **异步测试规则** (pytest-asyncio + SQLAlchemy Async)
   - 每个测试使用独立引擎（function scope）避免连接池冲突
   - 使用async_sessionmaker创建会话工厂
   - 必须在pytest.ini中配置asyncio_mode=auto
   - conftest.py中正确使用@pytest_asyncio.fixture装饰器
   - 连接池配置：pool_size=1, max_overflow=0 (测试环境)

3. **Session管理规则**
   - 测试中使用flush()代替commit()保持数据在事务中
   - 使用嵌套事务（async with session.begin()）自动回滚
   - 标准模式：session.begin() -> yield -> rollback() -> close()
   - 不要在测试fixture中手动commit，会导致状态问题

4. **测试数据规则**
   - 使用UUID生成唯一标识符避免唯一性约束冲突
   - 重复运行测试时数据必须唯一（用户名、客户代码、权限代码等）

5. **模块导入规则**
   - pytest.ini仅配置（asyncio_mode），不导入模块
   - 所有模块导入在conftest.py中完成
   - 避免重复导入导致冲突

### Security
- Never commit secrets, API keys, or credentials
- Validate and sanitize all user inputs
- Follow principle of least privilege
- Keep dependencies updated

## Additional Notes

- This file should be updated as the project grows
- Check for technology-specific configuration files for additional conventions
- When adding new features, maintain consistency with existing code style
