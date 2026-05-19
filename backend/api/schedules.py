from fastapi import APIRouter, HTTPException, Depends
from auth.routes import get_current_user, get_auth_manager
from typing import Dict, Any, List
from logger import logger

schedules_router = APIRouter(prefix="/api/schedules", tags=["schedules"])
ALLOWED_SCHEDULE_SAVE_FIELDS = {"schedule_name", "schedule_data", "constraints_data", "original_course_options"}
REQUIRED_SCHEDULE_SAVE_FIELDS = {"schedule_name", "schedule_data"}

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
        unknown_fields = set(data.keys()) - ALLOWED_SCHEDULE_SAVE_FIELDS
        if unknown_fields:
            raise HTTPException(
                status_code=422,
                detail=f"Unexpected fields: {', '.join(sorted(unknown_fields))}"
            )

        missing_fields = REQUIRED_SCHEDULE_SAVE_FIELDS - set(data.keys())
        if missing_fields:
            raise HTTPException(
                status_code=422,
                detail=f"Missing required fields: {', '.join(sorted(missing_fields))}"
            )

        insert_payload = {key: data[key] for key in ALLOWED_SCHEDULE_SAVE_FIELDS if key in data}
        insert_payload['user_id'] = user_id

        client = auth_manager.get_client_for_user(user_id)
        result = client.table("saved_schedules").insert(insert_payload).execute()
        return {"message": "Schedule saved", "schedule": result.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("save_schedule_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to save schedule")
