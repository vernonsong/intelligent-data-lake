from fastapi import APIRouter

router = APIRouter()

@router.get("")
async def list_skills():
    """获取 Skill 列表"""
    pass

@router.get("/{skill_id}")
async def get_skill(skill_id: str):
    """获取 Skill 详情"""
    pass
