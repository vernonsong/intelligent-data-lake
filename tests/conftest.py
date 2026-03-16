"""pytest 配置"""
import asyncio

def run_async(coro):
    """运行异步函数"""
    return asyncio.get_event_loop().run_until_complete(coro)
