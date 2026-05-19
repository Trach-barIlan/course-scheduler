from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, time as time_obj

class UserProfile(BaseModel):
    id: Optional[str] = None
    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

class Course(BaseModel):
    id: Optional[str] = None
    name: str
    lectures: List[str] = []
    ta_times: List[str] = []
    university_id: Optional[int] = 1
    department_id: Optional[int] = None
    academic_year: Optional[str] = "2024-2025"
    credits: Optional[float] = None
    is_active: bool = True
    additional_properties: Dict[str, Any] = {}

class CourseEvent(BaseModel):
    id: str
    course_id: str
    category_id: Optional[int] = None
    group_number: Optional[str] = None
    is_online: bool = False
    is_active: bool = True
    additional_properties: Dict[str, Any] = {}

class TimeSlot(BaseModel):
    id: Optional[int] = None
    course_event_id: str
    semester_id: int
    day_of_week_id: int
    start_time: str # Store as HH:MM:SS for Supabase compat
    end_time: str
    is_cancelled: bool = False

class Constraint(BaseModel):
    type: str
    time: Optional[int] = None
    day: Optional[str] = None
    name: Optional[str] = None

class ParseRequest(BaseModel):
    text: str

class SchedulePreference(BaseModel):
    type: str = "balanced"
    max_days: Optional[int] = None
    min_gaps: bool = False

class ScheduleRequest(BaseModel):
    courses: List[Course]
    constraints: List[Constraint]
    preference: Optional[str] = None
    preferences: Optional[SchedulePreference] = Field(default_factory=SchedulePreference)

class ParseLiveResponse(BaseModel):
    label: str
    color: str
    type: str

class ParseResponse(BaseModel):
    constraints: List[Constraint]
    entities: List[Dict[str, str]]
