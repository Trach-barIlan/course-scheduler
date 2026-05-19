from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Any, Dict
import time
import traceback
import os

from config import settings
from logger import logger, setup_logging
from ai_model.gliner_parser import GlinerParser
from schedule.logic import generate_schedule
from schedule.utils import parse_time_slot
from auth.routes import auth_router
from api.university import university_router
from api.statistics import statistics_router
from api.schedules import schedules_router
from api.contact import contact_router
from api.courses import courses_router

from models.schemas import (
    ParseRequest, ScheduleRequest, ParseLiveResponse, ParseResponse
)

# Setup structured logging
setup_logging()

app = FastAPI(
    title="Schedgic API",
    description="Modern course scheduler backend",
    version="2.0.0"
)

app.include_router(auth_router)
app.include_router(university_router)
app.include_router(statistics_router)
app.include_router(schedules_router)
app.include_router(contact_router)
app.include_router(courses_router)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Parser Instance
schedule_parser = None

@app.on_event("startup")
async def startup_event():
    global schedule_parser
    logger.info("app_startup", message="Initializing services...")
    if not settings.SKIP_AI_MODEL:
        try:
            schedule_parser = GlinerParser()
            logger.info("ai_model_loaded", status="success")
        except Exception as e:
            logger.error("ai_model_load_failed", error=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@app.post("/api/parse-live", response_model=List[ParseLiveResponse])
async def parse_live(request: ParseRequest):
    """Lightweight endpoint for real-time feedback."""
    if not schedule_parser:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail="AI model not available"
        )
        
    text = request.text.strip()
    if len(text) < 3:
        return []
    
    try:
        result = schedule_parser.parse(text, threshold=0.4)
        constraints = result.get("constraints", [])
        
        pills = []
        for c in constraints:
            if c["type"] == "no_classes_before":
                pills.append({"label": f"Starts after {c['time']}:00", "color": "blue", "type": c["type"]})
            elif c["type"] == "no_classes_after":
                pills.append({"label": f"Ends by {c['time']}:00", "color": "purple", "type": c["type"]})
            elif c["type"] == "no_day":
                pills.append({"label": f"No {c['day']}", "color": "red", "type": c["type"]})
            elif c["type"] == "avoid_ta":
                pills.append({"label": f"Avoid {c['name']}", "color": "orange", "type": c["type"]})

        return pills
    except Exception as e:
        logger.error("parse_live_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=str(e)
        )

@app.post("/api/parse", response_model=ParseResponse)
async def parse_input(request: ParseRequest):
    """Standard NLP parsing endpoint."""
    if not schedule_parser:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail="AI model not available"
        )
        
    try:
        result = schedule_parser.parse(request.text)
        constraints = result.get("constraints", [])
        raw_entities = result.get("raw_entities", [])
        
        formatted_constraints = []
        for c in constraints:
            if c["type"] == "no_classes_before":
                formatted_constraints.append({"type": "No Class Before", "time": c["time"]})
            elif c["type"] == "no_classes_after":
                formatted_constraints.append({"type": "No Class After", "time": c["time"]})
            elif c["type"] == "no_day":
                formatted_constraints.append({"type": "No Class Day", "day": c["day"]})
            elif c["type"] == "avoid_ta":
                formatted_constraints.append({"type": "Avoid TA", "name": c["name"]})

        return {
            "constraints": formatted_constraints,
            "entities": [
                {"specifics": ent["text"], "label": ent["label"]} 
                for ent in raw_entities
            ]
        }
    except Exception as e:
        logger.error("parse_input_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Parsing failed: {str(e)}"
        )

@app.post("/api/schedule")
async def api_schedule(payload: ScheduleRequest, request: Request):
    """Main schedule generation endpoint."""
    start_time = time.time()
    
    try:
        logger.info("generation_started", course_count=len(payload.courses))
        
        # Transform Pydantic courses to the format expected by the logic engine
        # (Parsing string time slots like "Mon 9-11" into tuples)
        parsed_courses = []
        for c in payload.courses:
            parsed_courses.append({
                "name": c.name,
                "lectures": [parse_time_slot(s) for s in c.lectures if s and parse_time_slot(s)],
                "ta_times": [parse_time_slot(s) for s in c.ta_times if s and parse_time_slot(s)]
            })
        
        constraints_dict = [c.dict() for c in payload.constraints]
        
        # Correctly map arguments: (courses, preference_string, constraints_list)
        pref_type = "crammed"
        if payload.preferences and payload.preferences.type:
            pref_type = payload.preferences.type
        elif getattr(payload, "preference", None):
            pref_type = payload.preference
        
        generated_list = generate_schedule(parsed_courses, pref_type, constraints_dict)

        
        duration_ms = int((time.time() - start_time) * 1000)
        
        if generated_list is None:
            logger.info("generation_finished", duration_ms=duration_ms, status="failed")
            return {"status": "error", "error": "No valid schedule found with these constraints", "message": "No valid schedule found with these constraints"}

        logger.info("generation_finished", duration_ms=duration_ms, status="success")
        return {"status": "success", "schedule": generated_list}

    except Exception as e:
        logger.error("generation_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
