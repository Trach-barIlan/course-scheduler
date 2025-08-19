#!/usr/bin/env python3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print('Environment check:')
print('SUPABASE_URL:', 'SET' if os.environ.get('SUPABASE_URL') else 'NOT SET')
print('SUPABASE_ANON_KEY:', 'SET' if os.environ.get('SUPABASE_ANON_KEY') else 'NOT SET') 
print('SUPABASE_SERVICE_ROLE_KEY:', 'SET' if os.environ.get('SUPABASE_SERVICE_ROLE_KEY') else 'NOT SET')

try:
    print('\nTesting imports...')
    from auth.auth_manager import AuthManager
    print('✅ AuthManager imported')
except Exception as e:
    print('❌ AuthManager failed:', str(e))

try:
    print('Testing AI model import...')
    from ai_model.ml_parser import ScheduleParser
    print('✅ ScheduleParser imported')
    parser = ScheduleParser()
    print('✅ ScheduleParser initialized')
except Exception as e:
    print('❌ ScheduleParser failed:', str(e))
    import traceback
    traceback.print_exc()

try:
    print('Testing Flask app import (without AI)...')
    # Skip AI model for now
    import os
    os.environ['SKIP_AI_MODEL'] = '1'
    from app import app
    print('✅ Flask app imported')
except Exception as e:
    print('❌ Flask app failed:', str(e))
    import traceback
    traceback.print_exc()
