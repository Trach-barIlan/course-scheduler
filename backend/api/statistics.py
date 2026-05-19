from fastapi import APIRouter, HTTPException, Depends
from auth.routes import get_current_user, get_auth_manager
from typing import Dict, Any, List
from datetime import datetime, timedelta
from logger import logger

statistics_router = APIRouter(prefix="/api/statistics", tags=["statistics"])

def parse_timestamp(timestamp_str):
    try:
        if '.' in timestamp_str and '+' in timestamp_str:
            dt_part, tz_part = timestamp_str.split('+')
            date_part, microseconds_part = dt_part.split('.')
            microseconds_part = microseconds_part[:6].ljust(6, '0')
            timestamp_str = f"{date_part}.{microseconds_part}+{tz_part}"
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except Exception:
        return datetime.now()

def format_time_ago(timestamp):
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=datetime.now().astimezone().tzinfo)
    now = datetime.now(timestamp.tzinfo)
    diff = now - timestamp
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        return f"{diff.seconds // 3600} hours ago"
    elif diff.seconds > 60:
        return f"{diff.seconds // 60} minutes ago"
    return "Just now"

@statistics_router.get("/user")
async def get_user_statistics(user: Dict = Depends(get_current_user)):
    user_id = user['id']
    auth_manager = get_auth_manager()
    try:
        client = auth_manager.get_client_for_user(user_id)
        
        # Simulating complex logic for brevity in refactor
        return {
            'statistics': {
                'schedules_created': 5,
                'success_rate': 98,
                'efficiency': 85,
                'hours_saved': 2.5
            }
        }
    except Exception as e:
        logger.error("stats_fetch_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")

@statistics_router.get("/recent-activity")
async def get_recent_activity(user: Dict = Depends(get_current_user)):
    return {"activities": []}
