"""日志配置 - 结构化日志"""

import logging
import sys
from typing import Optional
from datetime import datetime

try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False


def setup_logging(
    level: str = "INFO",
    log_format: str = "json",
    log_file: Optional[str] = None
) -> None:
    """
    设置日志配置
    
    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: 日志格式 (json, console)
        log_file: 日志文件路径 (可选)
    """
    
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # 创建根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # 清除现有处理器
    root_logger.handlers.clear()
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    if log_format == "json" and STRUCTLOG_AVAILABLE:
        # JSON 格式 (结构化日志)
        setup_structlog(console_handler)
    else:
        # 控制台格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # 文件处理器 (可选)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def setup_structlog(handler: logging.Handler) -> None:
    """设置 structlog 结构化日志"""
    if not STRUCTLOG_AVAILABLE:
        return
    
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str):
    """获取日志记录器"""
    if STRUCTLOG_AVAILABLE:
        return structlog.get_logger(name)
    else:
        return logging.getLogger(name)


# 日志工具函数
def log_api_call(
    logger,
    method: str,
    url: str,
    status_code: int,
    duration_ms: float,
    error: Optional[str] = None
):
    """记录 API 调用日志"""
    log_data = {
        "event": "api_call",
        "method": method,
        "url": url,
        "status_code": status_code,
        "duration_ms": duration_ms,
        "level": "error" if error else "info"
    }
    
    if error:
        log_data["error"] = error
        logger.error("API 调用失败", **log_data)
    else:
        logger.info("API 调用成功", **log_data)


def log_validation_step(
    logger,
    step_name: str,
    passed: bool,
    details: str,
    duration_ms: float
):
    """记录验证步骤日志"""
    log_data = {
        "event": "validation_step",
        "step": step_name,
        "passed": passed,
        "details": details,
        "duration_ms": duration_ms
    }
    
    if passed:
        logger.info("验证步骤通过", **log_data)
    else:
        logger.warning("验证步骤失败", **log_data)


def log_workflow_node(
    logger,
    node_id: str,
    node_type: str,
    status: str,
    message: str,
    context: Optional[dict] = None
):
    """记录工作流节点日志"""
    log_data = {
        "event": "workflow_node",
        "node_id": node_id,
        "node_type": node_type,
        "status": status,
        "message": message
    }
    
    if context:
        log_data["context"] = context
    
    if status == "error":
        logger.error("工作流节点错误", **log_data)
    elif status == "warning":
        logger.warning("工作流节点警告", **log_data)
    else:
        logger.info("工作流节点执行", **log_data)
