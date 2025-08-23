# 股票分析定时任务

## 功能说明

此定时任务系统可以自动在指定时间执行股票分析程序（`do_execute()`函数）。

## 安装依赖

确保已安装以下Python库：
```bash
pip install schedule
```

## 使用方法

### 方法一：使用批处理文件（推荐）
1. 双击运行 `start_scheduler.bat`
2. 程序会自动检查并安装所需依赖
3. 定时任务将在后台运行

### 方法二：手动运行
```bash
cd f:\langchian\demo\graph_demo
python schedule_task.py
```

## 定时设置

当前配置的执行时间：
- **09:30** - 股市开盘后分析
- **15:00** - 股市收盘后分析

## 修改定时设置

编辑 `schedule_task.py` 文件中的定时规则：

```python
# 每天上午9点30分执行
schedule.every().day.at("09:30").do(run_stock_analysis)

# 每天下午15点执行  
schedule.every().day.at("15:00").do(run_stock_analysis)

# 可以添加更多定时规则，例如：
# schedule.every().hour.at(":30").do(run_stock_analysis)  # 每小时的30分执行
# schedule.every(2).hours.do(run_stock_analysis)  # 每2小时执行一次
```

## Windows任务计划程序配置（可选）

如果需要系统级别的定时任务，可以使用Windows任务计划程序：

1. 打开"任务计划程序"
2. 创建新任务
3. 设置触发器（每天9:30和15:00）
4. 操作：启动程序 `python.exe`
5. 参数：`f:\langchian\demo\graph_demo\schedule_task.py`
6. 起始于：`f:\langchian\demo\graph_demo`

## 日志输出

程序运行日志会输出到控制台，包含：
- 执行时间戳
- 执行状态（成功/失败）
- 错误信息（如果有）

## 停止程序

- 在控制台中按 `Ctrl+C` 停止程序
- 如果是后台运行，需要结束Python进程

## 注意事项

1. 确保网络连接正常（需要访问股票数据API）
2. 确保代理设置正确（如需要）
3. 程序运行时间较长，请耐心等待
4. 建议在非交易时间测试，避免影响正常交易分析