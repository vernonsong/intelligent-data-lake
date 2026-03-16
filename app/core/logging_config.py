"""日志配置 - 简化版"""

import logging
import sys
from typing import Optional


def get_logger(name: str) -> logging.Logger:
    """获取 logger"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


def log_api_call(logger, method: str, url: str, status_code: int, duration_ms: float, error: str = None):
    """记录 API 调用日志"""
    msg = f"API: {method} {url} - {status_code} ({duration_ms:.1f}ms)"
    if error:
        logger.error(f"{msg} - {error}")
    else:
        logger.info(msg)


def log_validation_step(logger, step_name: str, passed: bool, details: str, duration_ms: float):
    """记录验证步骤日志"""
    status = "通过" if passed else "失败"
    logger.info(f"验证：{step_name} - {status} - {details} ({duration_ms:.1f}ms)")


def log_workflow_node(logger, node_id: str, node_type: str, status: str, message: str = None, context: dict = None):
    """记录工作流节点日志"""
    msg = f"工作流：{node_id} ({node_type}) - {status}"
    if message:
        msg += f" - {message}"
    
    if status == "error":
        logger.error(msg)
    elif status == "warning":
        logger.warning(msg)
    else:
        logger.info(msg)
