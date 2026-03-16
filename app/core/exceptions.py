"""异常类型定义 - 智能入湖系统专用异常"""


class IntelligentDataLakeError(Exception):
    """智能入湖系统基础异常"""
    def __init__(self, message: str, code: str = None, details: dict = None):
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "error": self.code,
            "message": self.message,
            "details": self.details
        }


class NetworkError(IntelligentDataLakeError):
    """网络错误 - API 调用失败"""
    def __init__(self, message: str, url: str = None, status_code: int = None):
        details = {"url": url, "status_code": status_code}
        super().__init__(message, code="NETWORK_ERROR", details=details)


class DataError(IntelligentDataLakeError):
    """数据错误 - 数据验证失败或数据不一致"""
    def __init__(self, message: str, field: str = None, value: any = None):
        details = {"field": field, "value": value}
        super().__init__(message, code="DATA_ERROR", details=details)


class BusinessError(IntelligentDataLakeError):
    """业务错误 - 业务规则违反"""
    def __init__(self, message: str, rule: str = None, constraint: str = None):
        details = {"rule": rule, "constraint": constraint}
        super().__init__(message, code="BUSINESS_ERROR", details=details)


class WorkflowError(IntelligentDataLakeError):
    """工作流错误 - 工作流执行失败"""
    def __init__(self, message: str, node_id: str = None, node_type: str = None):
        details = {"node_id": node_id, "node_type": node_type}
        super().__init__(message, code="WORKFLOW_ERROR", details=details)


class ValidationError(IntelligentDataLakeError):
    """验证错误 - 验证步骤失败"""
    def __init__(self, message: str, step: str = None, expected: any = None, actual: any = None):
        details = {"step": step, "expected": expected, "actual": actual}
        super().__init__(message, code="VALIDATION_ERROR", details=details)


class NotFoundError(IntelligentDataLakeError):
    """资源不存在错误"""
    def __init__(self, resource_type: str = None, resource_id: str = None):
        message = f"{resource_type}不存在"
        details = {"resource_type": resource_type, "resource_id": resource_id}
        super().__init__(message, code="NOT_FOUND", details=details)


class ConfigurationError(IntelligentDataLakeError):
    """配置错误"""
    def __init__(self, message: str, config_key: str = None):
        details = {"config_key": config_key}
        super().__init__(message, code="CONFIGURATION_ERROR", details=details)
