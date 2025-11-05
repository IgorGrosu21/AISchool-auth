from fastapi import APIRouter

router = APIRouter(tags=["worker"])

@router.get("/worker", include_in_schema=False)
async def worker():
    """Worker endpoint (excluded from schema in original)"""
    return {}

