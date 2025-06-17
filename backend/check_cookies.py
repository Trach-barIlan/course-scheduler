from itsdangerous import URLSafeTimedSerializer
import os
secret_key = os.environ.get('FLASK_SECRET_KEY', 'default-secret-key')  # Replace with your actual secret key
cookie_value = 'eyJfcGVybWFuZW50Ijp0cnVlfQ.aFGc4Q.eKIJPUbbephDtVGkIhues_9iL2U'  # Replace with the value of the cookie

serializer = URLSafeTimedSerializer(secret_key)
session_data = serializer.loads(cookie_value)
print(session_data)