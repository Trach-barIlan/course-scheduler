from fastapi import APIRouter, HTTPException, Depends
from auth.routes import get_current_user, get_auth_manager
from typing import Dict, Any, List
from datetime import datetime, timedelta, timezone
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


def _extract_count(result: Any) -> int:
    """Extract count from Supabase responses safely across client versions."""
    count = getattr(result, "count", None)
    if count is not None:
        return int(count)

    data = getattr(result, "data", None)
    if isinstance(data, list):
        return len(data)
    return 0


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except Exception:
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default

@statistics_router.get("/user")
async def get_user_statistics(user: Dict = Depends(get_current_user)):
    user_id = user["id"]
    auth_manager = get_auth_manager()

    try:
        client = auth_manager.get_client_for_user(user_id)

        stats_result = client.table("user_statistics").select("*").eq("user_id", user_id).limit(1).execute()
        stats_row = stats_result.data[0] if stats_result.data else {}

        # Primary counters from persisted stats table.
        schedules_created = _safe_int(stats_row.get("schedules_created_total"), 0)
        schedules_this_week = _safe_int(stats_row.get("schedules_created_this_week"), 0)
        total_courses_scheduled = _safe_int(stats_row.get("total_courses_scheduled"), 0)
        constraints_used_count = _safe_int(stats_row.get("constraints_used_count"), 0)
        average_generation_time = round(_safe_float(stats_row.get("average_schedule_generation_time"), 0.0), 2)
        preferred_schedule_type = stats_row.get("preferred_schedule_type") or "crammed"

        # Saved schedules count.
        saved_result = (
            client.table("saved_schedules")
            .select("id", count="exact", head=True)
            .eq("user_id", user_id)
            .execute()
        )
        saved_schedules_count = _extract_count(saved_result)

        # Use logs for success-rate calculations and fallback values.
        logs_sample_result = (
            client.table("schedule_generation_logs")
            .select("success, courses_count, constraints_count, generation_time_ms, schedule_type, created_at")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(200)
            .execute()
        )
        logs_sample = logs_sample_result.data or []

        total_logs_result = (
            client.table("schedule_generation_logs")
            .select("id", count="exact", head=True)
            .eq("user_id", user_id)
            .execute()
        )
        total_generations = _extract_count(total_logs_result)

        success_logs_result = (
            client.table("schedule_generation_logs")
            .select("id", count="exact", head=True)
            .eq("user_id", user_id)
            .eq("success", True)
            .execute()
        )
        successful_generations = _extract_count(success_logs_result)

        if total_generations == 0 and logs_sample:
            total_generations = len(logs_sample)
        if successful_generations == 0 and logs_sample:
            successful_generations = sum(1 for log in logs_sample if bool(log.get("success")))

        if schedules_created == 0 and total_generations > 0:
            schedules_created = total_generations

        if total_courses_scheduled == 0 and logs_sample:
            total_courses_scheduled = sum(_safe_int(log.get("courses_count"), 0) for log in logs_sample)

        if constraints_used_count == 0 and logs_sample:
            constraints_used_count = sum(_safe_int(log.get("constraints_count"), 0) for log in logs_sample)

        if average_generation_time <= 0 and logs_sample:
            times = [_safe_int(log.get("generation_time_ms"), 0) for log in logs_sample if _safe_int(log.get("generation_time_ms"), 0) > 0]
            if times:
                average_generation_time = round(sum(times) / len(times), 2)

        if preferred_schedule_type == "crammed" and logs_sample:
            schedule_types: Dict[str, int] = {}
            for log in logs_sample:
                schedule_type = log.get("schedule_type")
                if not schedule_type:
                    continue
                schedule_types[schedule_type] = schedule_types.get(schedule_type, 0) + 1
            if schedule_types:
                preferred_schedule_type = max(schedule_types, key=schedule_types.get)

        if schedules_this_week == 0 and logs_sample:
            now = datetime.now(timezone.utc)
            week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
            schedules_this_week = 0
            for log in logs_sample:
                created_at = log.get("created_at")
                if not created_at:
                    continue
                if parse_timestamp(created_at) >= week_start:
                    schedules_this_week += 1

        success_rate = round((successful_generations / total_generations) * 100) if total_generations > 0 else 0
        efficiency = success_rate

        # Estimated from a 30-minute manual scheduling baseline per generated schedule.
        hours_saved = round(schedules_created * 0.5, 1)

        return {
            "statistics": {
                "schedules_created": schedules_created,
                "schedules_this_week": schedules_this_week,
                "saved_schedules_count": saved_schedules_count,
                "hours_saved": hours_saved,
                "success_rate": success_rate,
                "efficiency": efficiency,
                "total_courses_scheduled": total_courses_scheduled,
                "preferred_schedule_type": preferred_schedule_type,
                "constraints_used_count": constraints_used_count,
                "average_generation_time": average_generation_time,
            }
        }
    except Exception as e:
        logger.error("stats_fetch_failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")

@statistics_router.get("/recent-activity")
async def get_recent_activity(user: Dict = Depends(get_current_user)):
    user_id = user["id"]
    auth_manager = get_auth_manager()

    try:
        client = auth_manager.get_client_for_user(user_id)

        logs_result = (
            client.table("schedule_generation_logs")
            .select("success, courses_count, constraints_count, schedule_type, error_message, created_at")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(10)
            .execute()
        )
        schedules_result = (
            client.table("saved_schedules")
            .select("id, schedule_name, created_at")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(10)
            .execute()
        )

        activities: List[Dict[str, Any]] = []

        for log in logs_result.data or []:
            timestamp_raw = log.get("created_at")
            timestamp = parse_timestamp(timestamp_raw) if timestamp_raw else datetime.now(timezone.utc)
            success = bool(log.get("success"))
            course_count = _safe_int(log.get("courses_count"), 0)
            schedule_type = log.get("schedule_type") or "unknown"

            if success:
                action = f"Generated {course_count} course schedule ({schedule_type})"
            else:
                error_message = (log.get("error_message") or "Generation failed").strip()
                action = f"Failed schedule generation: {error_message}"

            activities.append(
                {
                    "type": "generation",
                    "success": success,
                    "action": action,
                    "time": format_time_ago(timestamp),
                    "timestamp": timestamp.isoformat(),
                }
            )

        for schedule in schedules_result.data or []:
            timestamp_raw = schedule.get("created_at")
            timestamp = parse_timestamp(timestamp_raw) if timestamp_raw else datetime.now(timezone.utc)
            schedule_name = schedule.get("schedule_name") or "Untitled schedule"

            activities.append(
                {
                    "type": "save",
                    "success": True,
                    "action": f"Saved schedule: {schedule_name}",
                    "time": format_time_ago(timestamp),
                    "timestamp": timestamp.isoformat(),
                }
            )

        activities.sort(key=lambda item: item.get("timestamp", ""), reverse=True)
        for activity in activities:
            activity.pop("timestamp", None)

        return {"activities": activities[:20]}
    except Exception as e:
        logger.error("recent_activity_fetch_failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch recent activity")
