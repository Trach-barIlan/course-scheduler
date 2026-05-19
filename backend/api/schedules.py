from fastapi import APIRouter, HTTPException, Depends
from auth.routes import get_current_user, get_auth_manager
from typing import Dict, Any, List
from logger import logger

schedules_router = APIRouter(prefix="/api/schedules", tags=["schedules"])

@schedules_router.get("/")
async def get_saved_schedules(user: Dict = Depends(get_current_user)):
    user_id = user['id']
    auth_manager = get_auth_manager()
    try:
        client = auth_manager.get_client_for_user(user_id)
        result = client.table("saved_schedules").select("*").eq("user_id", user_id).execute()
        return {"schedules": result.data}
    except Exception as e:
        logger.error("fetch_schedules_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch schedules")

@schedules_router.post("/")
async def save_schedule(data: Dict[str, Any], user: Dict = Depends(get_current_user)):
    user_id = user['id']
    auth_manager = get_auth_manager()
    try:
        client = auth_manager.get_client_for_user(user_id)
        data['user_id'] = user_id
        result = client.table("saved_schedules").insert(data).execute()
        return {"message": "Schedule saved", "schedule": result.data[0]}
    except Exception as e:
        logger.error("save_schedule_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to save schedule")
