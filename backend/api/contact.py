from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, Optional
from datetime import datetime
from logger import logger
from auth.routes import get_auth_manager

contact_router = APIRouter(prefix="/api", tags=["contact"])

class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    subject: str
    type: str
    message: str
    university: Optional[str] = None
    course: Optional[str] = None
    userAgent: Optional[str] = None
    timestamp: Optional[Any] = None

@contact_router.post("/contact")
async def submit_contact_form(data: ContactRequest, request: Request):
    """Handle contact form submission."""
    try:
        contact_submission = {
            'name': data.name.strip()[:100],
            'email': str(data.email).strip()[:255],
            'subject': data.subject.strip()[:200],
            'type': data.type.strip()[:50],
            'message': data.message.strip()[:2000],
            'university': data.university.strip()[:100] if data.university else None,
            'course': data.course.strip()[:100] if data.course else None,
            'user_agent': data.userAgent.strip()[:500] if data.userAgent else None,
            'ip_address': request.client.host,
            'submitted_at': datetime.utcnow().isoformat(),
            'status': 'new',
            'additional_data': {
                'timestamp': data.timestamp,
                'form_version': '2.0 (FastAPI)'
            }
        }
        
        auth_manager = get_auth_manager()
        client = auth_manager.service_supabase
        
        result = client.table('contact_submissions').insert(contact_submission).execute()
        
        if result.data:
            logger.info("contact_form_submitted", name=data.name, subject=data.subject)
            return {
                'success': True,
                'message': 'Thank you for your message! We will get back to you soon.',
                'submission_id': result.data[0]['id']
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save submission")
            
    except Exception as e:
        logger.error("contact_form_error", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@contact_router.get("/contact/stats")
async def get_contact_stats():
    auth_manager = get_auth_manager()
    client = auth_manager.service_supabase
    result = client.table('contact_submissions').select('type, status').execute()
    return {'success': True, 'total': len(result.data)}
