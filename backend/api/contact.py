#!/usr/bin/env python3
"""
Contact form API endpoints
"""

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create blueprint
contact_bp = Blueprint('contact', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")

def get_supabase_client():
    """Get Supabase client with service role key"""
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        logger.error("Missing Supabase configuration")
        return None
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

@contact_bp.route('/contact', methods=['POST'])
def submit_contact_form():
    """Handle contact form submission"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'subject', 'type', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Sanitize and prepare data
        contact_submission = {
            'name': data.get('name', '').strip()[:100],
            'email': data.get('email', '').strip()[:255],
            'subject': data.get('subject', '').strip()[:200],
            'type': data.get('type', '').strip()[:50],
            'message': data.get('message', '').strip()[:2000],
            'university': data.get('university', '').strip()[:100] if data.get('university') else None,
            'course': data.get('course', '').strip()[:100] if data.get('course') else None,
            'user_agent': data.get('userAgent', '').strip()[:500] if data.get('userAgent') else None,
            'ip_address': request.remote_addr,
            'submitted_at': datetime.utcnow().isoformat(),
            'status': 'new',
            'additional_data': {
                'timestamp': data.get('timestamp'),
                'form_version': '1.0'
            }
        }
        
        # Save to database
        supabase = get_supabase_client()
        if not supabase:
            logger.error("Failed to connect to Supabase")
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        # Insert into contact_submissions table
        result = supabase.table('contact_submissions').insert(contact_submission).execute()
        
        if result.data:
            logger.info(f"Contact form submitted successfully: {contact_submission['name']} - {contact_submission['subject']}")
            
            # Send notification email (optional - you can implement this later)
            # send_contact_notification(contact_submission)
            
            return jsonify({
                'success': True,
                'message': 'Thank you for your message! We will get back to you soon.',
                'submission_id': result.data[0]['id']
            }), 200
        else:
            logger.error("Failed to insert contact submission")
            return jsonify({
                'success': False,
                'error': 'Failed to save submission'
            }), 500
            
    except Exception as e:
        logger.error(f"Error processing contact form: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@contact_bp.route('/contact/submissions', methods=['GET'])
def get_contact_submissions():
    """Get contact submissions (admin endpoint)"""
    try:
        # This could be protected with admin authentication
        supabase = get_supabase_client()
        if not supabase:
            return jsonify({'error': 'Database connection failed'}), 500
        
        # Get query parameters
        limit = min(int(request.args.get('limit', 50)), 100)  # Max 100
        offset = int(request.args.get('offset', 0))
        status = request.args.get('status')
        type_filter = request.args.get('type')
        
        # Build query
        query = supabase.table('contact_submissions').select('*')
        
        if status:
            query = query.eq('status', status)
        if type_filter:
            query = query.eq('type', type_filter)
        
        # Execute query with pagination
        result = query.order('submitted_at', desc=True).range(offset, offset + limit - 1).execute()
        
        return jsonify({
            'success': True,
            'submissions': result.data,
            'count': len(result.data)
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching contact submissions: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch submissions'
        }), 500

@contact_bp.route('/contact/stats', methods=['GET'])
def get_contact_stats():
    """Get contact form statistics"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return jsonify({'error': 'Database connection failed'}), 500
        
        # Get submission counts by type
        result = supabase.table('contact_submissions').select('type, status').execute()
        
        stats = {
            'total': len(result.data),
            'by_type': {},
            'by_status': {}
        }
        
        for submission in result.data:
            # Count by type
            sub_type = submission.get('type', 'unknown')
            stats['by_type'][sub_type] = stats['by_type'].get(sub_type, 0) + 1
            
            # Count by status
            status = submission.get('status', 'unknown')
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching contact stats: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch statistics'
        }), 500
