import re

def validate_password(password):
    """Validate password meets security requirements."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    return True, None

def validate_email(email):
    """Validate email format."""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def validate_signup_fields(name, email, password, confirm_password):
    """Validate all signup form fields."""
    if not all([name, email, password, confirm_password]):
        return False, "Please fill in all fields"
        
    if not validate_email(email):
        return False, "Please enter a valid email address"
        
    if password != confirm_password:
        return False, "Passwords do not match"
        
    is_valid, error_msg = validate_password(password)
    if not is_valid:
        return False, error_msg
        
    return True, None
