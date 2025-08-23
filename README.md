# lang-chain-demo

基于LangChain和FastAPI的智能股票分析系统，集成了实时数据获取、AI分析和可视化展示功能。

## 🚀 功能特性

- 📊 **实时股票数据分析** - 通过akshare获取实时股票数据
- 🤖 **AI智能分析** - 使用LangChain和OpenAI进行深度分析
- 📈 **技术指标计算** - 集成TA-Lib进行技术分析
- ⏰ **定时任务** - 自动定时执行股票分析
- 🌐 **Web界面** - 基于React + Material-UI的现代化前端
- 📋 **分析结果管理** - 完整的分析历史记录和查询功能
- 🔒 **数据库存储** - 使用MySQL存储分析结果

## 🏗️ 项目结构

```
langchian/
├── demo/
│   ├── graph_demo/          # 定时任务模块
│   │   ├── models.py        # 数据库模型
│   │   ├── llm_init.py      # LLM初始化配置
│   │   ├── schedule_task.py # 定时任务逻辑
│   │   └── start_scheduler.bat # Windows启动脚本
│   ├── stock_trade/         # 股票交易API模块
│   │   └── stock_route.py   # FastAPI路由
│   ├── demo/               # 示例代码模块
│   │   └── demo_stock_info.py # 股票信息获取示例
│   ├── web/                # 前端项目
│   │   ├── src/
│   │   │   ├── App.tsx     # 主应用组件
│   │   │   ├── components/
│   │   │   │   ├── Sidebar.tsx      # 侧边栏
│   │   │   │   ├── AnalysisResults.tsx # 分析结果组件
│   │   │   │   └── Sidebar.css
│   │   ├── package.json    # 前端依赖配置
│   │   └── vite.config.ts  # Vite构建配置
│   ├── main.py             # FastAPI主应用
│   ├── setting.py          # 应用配置
│   ├── pyproject.toml      # Python依赖配置(uv)
│   └── README.md           # 项目说明
```

## 📦 技术栈

### 后端技术
- **Python 3.12+** - 主要编程语言
- **FastAPI** - 高性能Web框架
- **LangChain** - AI应用开发框架
- **OpenAI API** - 大语言模型服务
- **MySQL** - 关系型数据库
- **SQLAlchemy** - ORM框架
- **akshare** - 股票数据接口
- **TA-Lib** - 技术分析库
- **uv** - Python包管理工具

### 前端技术
- **React 19** - 用户界面库
- **TypeScript** - 类型安全的JavaScript
- **Material-UI (MUI)** - React组件库
- **Vite** - 前端构建工具
- **Axios** - HTTP客户端
- **Day.js** - 日期处理库

### 开发工具
- **UV** - 快速的Python包安装器
- **Vite** - 现代化的前端构建工具
- **ESLint** - 代码质量检查
- **TypeScript** - 类型检查

## 🔧 安装说明

### 前置要求
- Python 3.12+
- Node.js 18+
- MySQL 8.0+
- TA-Lib库 (需要预先安装)

### 后端安装

1. 克隆项目并进入目录：
```bash
cd f:\langchian\demo
```

2. 使用uv安装Python依赖：
```bash
uv sync
```

3. 配置数据库连接：
编辑 `setting.py` 文件，设置MySQL连接信息：
```python
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://username:password@localhost:3306/stock_analysis"
```

4. 配置OpenAI API密钥：
在 `setting.py` 中设置：
```python
base_url = "https://api.openai.com/v1"
api_key = "your-openai-api-key"
```

### 前端安装

1. 进入前端目录：
```bash
cd web
```

2. 安装Node.js依赖：
```bash
npm install
```

3. 启动开发服务器：
```bash
npm run dev
```

## 🚀 使用指南

### 启动后端服务
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8888
```

### 启动定时任务
```bash
cd graph_demo
start_scheduler_fixed.bat
```

### 访问Web界面
打开浏览器访问：http://localhost:5173

### API接口
- `POST /api/stock/agent` - 获取股票分析报告
- `POST /api/stock/ratings` - 获取投资评级列表
- `GET /api/stock/report/{symbol}` - 获取个股报告

## ⚙️ 配置说明

### 环境变量配置
创建 `.env` 文件（可选）：
```env
DATABASE_URL=mysql+mysqlconnector://user:password@localhost:3306/dbname
OPENAI_API_KEY=your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
```

### 定时任务配置
在 `schedule_task.py` 中可修改分析计划：
```python
# 每天09:30和15:00执行分析
schedule.every().day.at("09:30").do(run_stock_analysis)
schedule.every().day.at("15:00").do(run_stock_analysis)
```

## 🛠️ 开发指南

### 项目架构
项目采用模块化设计：
1. **API层** - FastAPI路由处理HTTP请求
2. **服务层** - 业务逻辑和数据处理
3. **数据层** - 数据库操作和模型定义
4. **AI层** - LangChain智能分析
5. **任务层** - 定时任务调度

### 添加新的分析指标
1. 在 `llm_init.py` 中扩展分析工具
2. 在 `schedule_task.py` 中更新分析逻辑
3. 在前端组件中增加展示界面

### 数据库迁移
使用Alembic进行数据库迁移：
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## 🐛 故障排除

### 常见问题

1. **TA-Lib安装失败**
   - 确保已安装TA-Lib的C库
   - 使用项目提供的wheel文件：`uv add ./ta_lib-0.6.4-cp312-cp312-win_amd64.whl`

2. **MySQL连接错误**
   - 检查MySQL服务是否启动
   - 验证数据库连接字符串格式

3. **OpenAI API错误**
   - 检查API密钥是否正确
   - 确认网络连接正常

4. **前端构建错误**
   - 清除node_modules重新安装：`rm -rf node_modules && npm install`

### 日志查看
后端日志位于控制台输出，前端错误可在浏览器开发者工具中查看。

## 📊 功能模块详解

### 股票分析模块
- **实时数据获取** - 通过akshare接口获取股票实时行情
- **技术指标计算** - 使用TA-Lib计算MACD、RSI等技术指标
- **AI智能分析** - LangChain整合多维度数据生成分析报告
- **风险评估** - 基于历史数据和市场情况评估风险等级

### 定时任务模块
- **自动执行** - 每天固定时间自动运行分析任务
- **结果存储** - 分析结果自动保存到数据库
- **错误重试** - 任务失败自动重试机制

### Web界面模块
- **响应式设计** - 支持桌面和移动端访问
- **数据可视化** - 图表展示分析结果
- **搜索过滤** - 支持按股票代码、名称、日期筛选
- **分页浏览** - 大数据集分页显示

## 🤝 贡献指南

1. Fork 本项目
2. 创建特性分支：`git checkout -b feature/AmazingFeature`
3. 提交更改：`git commit -m 'Add some AmazingFeature'`
4. 推送到分支：`git push origin feature/AmazingFeature`
5. 提交Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [akshare](https://github.com/akfamily/akshare) - 提供丰富的股票数据接口
- [LangChain](https://github.com/langchain-ai/langchain) - 优秀的AI应用开发框架
- [FastAPI](https://github.com/tiangolo/fastapi) - 高性能Python Web框架
- [Material-UI](https://mui.com/) - 优秀的React组件库

---

如有问题或建议，请提交Issue或联系开发团队。

## 功能特性

- 📊 股票数据获取和分析
- ⏰ 定时任务调度（每日开盘和收盘分析）
- 🤖 AI 驱动的股票分析报告
- 🗄️ MySQL 数据库存储
- 🌐 FastAPI Web 接口
- 📈 技术指标分析

## 项目结构

```
f:\langchian\demo\
├── demo\                 # 演示代码和工具
├── graph_demo\           # 图形化演示和定时任务
│   ├── schedule_task.py  # 定时任务脚本
│   ├── start_scheduler.bat # Windows 启动脚本
│   └── output\          # 分析结果输出
├── llm_stock\           # LLM 股票分析模块
├── stock_trade\         # 股票交易相关功能
├── web\                 # 前端界面
├── main.py              # FastAPI 主程序
├── setting.py           # 配置文件
└── pyproject.toml       # 项目依赖配置
```

## 安装说明

### 前置要求

- Python 3.8+
- MySQL 5.7+
- UV (Python 包管理器)

### 环境设置

1. 创建虚拟环境：
```bash
uv venv .venv
```

2. 激活虚拟环境：
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

3. 安装依赖：
```bash
uv pip install -e .
```

### 数据库配置

1. 创建 MySQL 数据库
2. 修改 `setting.py` 中的数据库连接配置
3. 初始化数据库：
```bash
python -m graph_demo.init_db
```

## 使用指南

### 启动定时任务

```bash
# 使用 bat 脚本（Windows）
cd graph_demo
start_scheduler_fixed.bat

# 手动启动
python graph_demo/schedule_task.py
```

定时任务会在每天 09:30（开盘后）和 15:00（收盘后）自动执行股票分析。

### 启动 Web 服务

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/docs 查看 API 文档。

### 手动执行股票分析

```bash
python demo/demo_stock_info.py
```

## 依赖库

主要依赖：
- FastAPI
- LangChain
- akshare (股票数据)
- schedule (定时任务)
- SQLAlchemy (数据库)
- TA-Lib (技术分析)

完整依赖见 `pyproject.toml`。

## 配置说明

### 主要配置文件

- `setting.py` - 应用配置（数据库、API密钥等）
- `pyproject.toml` - 项目依赖配置
- `uv.lock` - 依赖版本锁定

### 环境变量

设置以下环境变量或修改 `setting.py`：

```python
# 数据库配置
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "stock_analysis"
DB_USER = "your_username"
DB_PASSWORD = "your_password"

# API 密钥（可选）
OPENAI_API_KEY = "your_openai_key"
```

## 开发指南

### 添加新的股票数据源

1. 在 `demo/stock_tools.py` 中添加新的数据获取函数
2. 在 `graph_demo/schedule_task.py` 中集成到定时任务
3. 在 `llm_stock/` 中添加相应的分析逻辑

### 扩展定时任务

修改 `graph_demo/schedule_task.py` 中的调度配置：

```python
# 添加新的定时任务
schedule.every().day.at("10:00").do(your_new_task)
```

## 故障排除

### 常见问题

1. **MySQL 连接失败**：检查数据库配置和网络连接
2. **akshare 库安装失败**：尝试使用国内镜像源
3. **定时任务不执行**：检查系统时间和时区设置

### 日志查看

定时任务日志输出在控制台，分析结果保存在 `graph_demo/output/` 目录。

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！