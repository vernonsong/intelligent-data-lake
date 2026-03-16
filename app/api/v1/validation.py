from fastapi import APIRouter

router = APIRouter()

@router.post("/validate")
async def validate_workflow():
    """验证工作流 - SSE"""
    pass

@router.get("/reports/{report_id}")
async def get_report(report_id: str):
    """获取验证报告"""
    pass
