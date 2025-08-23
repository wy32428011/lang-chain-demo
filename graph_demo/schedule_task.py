import schedule
import time
import subprocess
import os
from datetime import datetime

# 设置工作目录为脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))

def run_stock_analysis():
    """执行股票分析程序"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始执行股票分析...")
    
    # 切换到脚本目录
    os.chdir(script_dir)
    
    # 执行llm_init.py中的do_execute函数
    try:
        # 使用subprocess运行Python脚本（使用虚拟环境的Python路径）
        result = subprocess.run([
            'f:\\langchian\\demo\\.venv\\Scripts\\python.exe', 'llm_init.py'
        ], capture_output=True, text=True, cwd=script_dir, env={
            **os.environ,
            'PYTHONPATH': 'f:\\langchian\\demo'
        })
        
        if result.returncode == 0:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 股票分析执行成功")
            print("输出:", result.stdout)
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 执行失败")
            print("错误:", result.stderr)
            
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 执行异常: {e}")

def main():
    """主函数，设置定时任务"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 股票分析定时任务启动")
    print("工作目录:", script_dir)
    
    # 设置定时任务
    # 每天上午9点30分执行（股市开盘时间）
    schedule.every().day.at("09:30").do(run_stock_analysis)
    
    # 每天下午15点执行（股市收盘时间）
    schedule.every().day.at("15:00").do(run_stock_analysis)
    
    print("定时任务已设置:")
    print("- 每天 09:30: 股市开盘后分析")
    print("- 每天 15:00: 股市收盘后分析")
    print("程序运行中，按 Ctrl+C 退出...")
    
    # 立即执行一次
    run_stock_analysis()
    
    # 保持程序运行
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 程序已退出")
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 程序异常退出: {e}")