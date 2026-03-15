# 贡献指南

感谢您对 freebSEngine 项目的关注！我们欢迎各种形式的贡献，包括但不限于代码、文档、测试、示例和问题报告。

## 开发环境设置

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/freebSEngine.git
cd freebSEngine
```

### 2. 安装 Rust

freebSEngine 使用 Rust 作为核心计算引擎。请安装 Rust 工具链：

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

### 3. 安装 Python 依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 安装开发依赖
pip install -e ".[dev]"
```

### 4. 安装 maturin

maturin 是构建 Rust-Python 混合包的工具：

```bash
pip install maturin
```

### 5. 构建项目

```bash
# 开发模式构建
maturin develop

# 或使用发布模式
maturin develop --release
```

## 开发工作流

### 1. 创建分支

```bash
git checkout -b feature/your-feature-name
```

### 2. 运行测试

```bash
# 运行 Python 测试
pytest tests/

# 运行 Rust 测试
cargo test

# 运行所有测试
python -m pytest tests/ && cargo test
```

### 3. 代码质量检查

```bash
# 代码格式化
black python/freebSEngine tests/ examples/

# 代码检查
ruff check python/freebSEngine tests/ examples/

# 类型检查
mypy python/freebSEngine tests/ examples/
```

### 4. 提交更改

```bash
git add .
git commit -m "描述你的更改"
git push origin feature/your-feature-name
```

### 5. 创建 Pull Request

在 GitHub 上创建 Pull Request，并确保：

- 描述清楚更改的内容和原因
- 关联相关的问题（如果有）
- 确保所有测试通过
- 更新相关文档

## 代码规范

### Rust 代码规范

1. **格式化**: 使用 `cargo fmt` 格式化代码
2. **代码检查**: 使用 `cargo clippy` 检查代码质量
3. **文档**: 为所有公共 API 添加文档注释
4. **错误处理**: 使用 `thiserror` 定义清晰的错误类型
5. **测试**: 为所有功能添加单元测试

### Python 代码规范

1. **格式化**: 使用 `black` 格式化代码
2. **代码检查**: 使用 `ruff` 检查代码质量
3. **类型提示**: 为所有函数添加类型提示
4. **文档**: 使用 Google 风格文档字符串
5. **测试**: 使用 `pytest` 编写测试

### 文档规范

1. **API 文档**: 为所有公共函数和类添加文档字符串
2. **示例**: 提供完整的使用示例
3. **README**: 保持 README.md 更新
4. **教程**: 为复杂功能编写教程

## 项目结构

```
freebSEngine/
├── Cargo.toml          # Rust 项目配置
├── pyproject.toml      # Python 项目配置
├── src/                # Rust 源代码
│   └── lib.rs          # 核心库
├── python/             # Python 包
│   └── freebSEngine/
│       ├── __init__.py # 包入口
│       ├── demo.py     # 可视化演示
│       ├── utils.py    # 工具函数
│       └── celestial_objects.py  # 天体对象
├── tests/              # 测试文件
├── examples/           # 使用示例
├── docs/               # 文档
└── .github/workflows/  # CI/CD 配置
```

## 添加新功能

### 1. 添加新的 Rust 函数

1. 在 `src/lib.rs` 中添加函数
2. 使用 `#[pyfunction]` 宏暴露给 Python
3. 在 `#[pymodule]` 函数中注册
4. 添加 Rust 单元测试

### 2. 添加新的 Python 模块

1. 在 `python/freebSEngine/` 目录下创建新模块
2. 在 `__init__.py` 中导出
3. 添加类型提示和文档
4. 添加 Python 单元测试

### 3. 添加可视化功能

1. 在 `demo.py` 中添加新的演示类或函数
2. 确保依赖是可选的（在 `pyproject.toml` 的 `visualization` 额外依赖中）
3. 提供交互式使用示例

## 测试指南

### 单元测试

- **Rust 测试**: 在 `src/` 目录中使用 `#[cfg(test)]` 模块
- **Python 测试**: 在 `tests/` 目录中编写 `test_*.py` 文件
- **测试覆盖率**: 目标达到 80% 以上的测试覆盖率

### 集成测试

- 测试 Rust 和 Python 之间的接口
- 测试完整的工作流程
- 测试性能基准

### 性能测试

```bash
# 运行 Rust 性能基准
cargo bench

# 运行 Python 性能测试
python -m pytest tests/ -m "performance"
```

## 文档指南

### 代码文档

```python
def calculate_orbit(r0: List[float], v0: List[float]) -> np.ndarray:
    """计算天体轨道
    
    Args:
        r0: 初始位置向量 [x, y, z] (米)
        v0: 初始速度向量 [vx, vy, vz] (米/秒)
        
    Returns:
        numpy.ndarray: 轨道位置数组，形状为 (n_steps, 3)
        
    Raises:
        ValueError: 如果输入向量长度不正确
        
    Examples:
        >>> r0 = [1.496e11, 0.0, 0.0]
        >>> v0 = [0.0, 29780.0, 0.0]
        >>> positions = calculate_orbit(r0, v0)
        >>> positions.shape
        (1000, 3)
    """
```

### 教程文档

1. **基础教程**: 介绍基本概念和使用方法
2. **高级教程**: 介绍高级功能和性能优化
3. **API 参考**: 完整的 API 文档
4. **示例**: 完整的工作示例

## 发布流程

### 1. 版本管理

使用语义化版本控制：

- **主版本号**: 不兼容的 API 更改
- **次版本号**: 向后兼容的功能性新增
- **修订号**: 向后兼容的问题修正

### 2. 发布检查清单

- [ ] 更新 `Cargo.toml` 和 `pyproject.toml` 中的版本号
- [ ] 更新 `CHANGELOG.md`
- [ ] 运行所有测试
- [ ] 更新文档
- [ ] 创建 Git 标签
- [ ] 构建发布包
- [ ] 发布到 PyPI

### 3. 自动发布

项目使用 GitHub Actions 自动发布到 PyPI。当创建 Git 标签时自动触发。

## 问题报告

### 报告 Bug

1. 使用 GitHub Issues
2. 描述清晰的问题现象
3. 提供复现步骤
4. 提供环境信息
5. 提供相关日志或错误信息

### 功能请求

1. 描述需要的功能
2. 说明使用场景
3. 提供参考实现或相关项目
4. 讨论实现方案

## 行为准则

本项目遵守 [贡献者公约行为准则](https://www.contributor-covenant.org/version/2/1/code_of_conduct/)。请确保你的行为符合该准则。

## 联系方式

- **问题追踪**: GitHub Issues
- **讨论**: GitHub Discussions
- **邮件**: team@freebSEngine.org

## 致谢

感谢所有贡献者的付出！你的每一份贡献都让这个项目变得更好。

---

*本指南根据项目发展可能会更新，请定期查看最新版本。*