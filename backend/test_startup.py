#!/usr/bin/env python3
import os
os.environ['SKIP_AI_MODEL'] = '1'

print('Testing basic imports...')

try:
    from flask import Flask
    print('✅ Flask imported')
except Exception as e:
    print('❌ Flask failed:', e)

try:
    from auth.routes import token_required
    print('✅ Auth imported')
except Exception as e:
    print('❌ Auth failed:', e)

try:
    from api.university import university_bp
    print('✅ University API imported')  
except Exception as e:
    print('❌ University API failed:', e)

try:
    from app import app
    print('✅ Flask app imported successfully!')
    print(f'App has {len(app.url_map._rules)} routes registered')
except Exception as e:
    print('❌ Flask app failed:', e)
    import traceback
    traceback.print_exc()
