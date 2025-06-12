import re

def validate_email_comprehensive(email):
    """Test comprehensive email validation"""
    print(f"Testing email: '{email}'")
    
    # Basic regex pattern
    pattern = r'^[a-zA-Z0-9.!#$%&\'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
    
    # Check basic pattern
    if not re.match(pattern, email):
        print("❌ Failed basic regex pattern")
        return False
    
    # Additional checks
    if email.count('@') != 1:
        print("❌ Must have exactly one @ symbol")
        return False
    
    local, domain = email.split('@')
    
    # Local part checks
    if len(local) == 0 or len(local) > 64:
        print(f"❌ Local part length invalid: {len(local)}")
        return False
    
    # Domain part checks
    if len(domain) == 0 or len(domain) > 255:
        print(f"❌ Domain part length invalid: {len(domain)}")
        return False
    
    # Domain must have at least one dot
    if '.' not in domain:
        print("❌ Domain must contain at least one dot")
        return False
    
    # Domain parts shouldn't be empty
    domain_parts = domain.split('.')
    if any(len(part) == 0 for part in domain_parts):
        print("❌ Domain parts cannot be empty")
        return False
    
    print("✅ Email validation passed")
    return True

# Test various email formats
test_emails = [
    "hi2@gmail.com",
    "test@example.com",
    "user.name@domain.co.uk",
    "user+tag@example.org",
    "invalid.email",
    "@invalid.com",
    "user@",
    "user@domain",
    "user@domain.",
    "user@.domain.com",
    ""
]

print("Email Validation Test Results:")
print("=" * 50)

for email in test_emails:
    validate_email_comprehensive(email)
    print("-" * 30)