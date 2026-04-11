import hashlib
import re
from datetime import datetime

class Auth:
    def __init__(self, database):
        self.db = database
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, stored_password, provided_password):
        """Verify password against stored hash"""
        return stored_password == self.hash_password(provided_password)
    
    def validate_email(self, email):
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None
    
    def validate_username(self, username):
        """Validate username format"""
        # Username should be 3-20 characters, alphanumeric and underscores only
        if len(username) < 3 or len(username) > 20:
            return False
        return re.match(r'^[a-zA-Z0-9_]+$', username) is not None
    
    def validate_password(self, password):
        """Validate password strength"""
        # Password should be at least 6 characters long
        if len(password) < 6:
            return False, "Password must be at least 6 characters long"
        
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        # Check for at least one digit
        if not re.search(r'[0-9]', password):
            return False, "Password must contain at least one number"
        
        return True, "Password is valid"
    
    def register_user(self, username, email, password):
        """Register a new user"""
        # Validate input
        if not username or not email or not password:
            return {'success': False, 'message': 'All fields are required'}
        
        # Validate username
        if not self.validate_username(username):
            return {'success': False, 'message': 'Username must be 3-20 characters, alphanumeric and underscores only'}
        
        # Validate email
        if not self.validate_email(email):
            return {'success': False, 'message': 'Please enter a valid email address'}
        
        # Validate password
        is_valid, message = self.validate_password(password)
        if not is_valid:
            return {'success': False, 'message': message}
        
        # Check if username already exists
        if self.db.find_user_by_username(username):
            return {'success': False, 'message': 'Username already exists'}
        
        # Check if email already exists
        if self.db.find_user_by_email(email):
            return {'success': False, 'message': 'Email already registered'}
        
        # Create user data
        user_data = {
            'username': username,
            'email': email,
            'password': self.hash_password(password),
            'created_at': datetime.utcnow(),
            'last_login': None,
            'is_active': True
        }
        
        # Insert user into database
        user_id = self.db.create_user(user_data)
        if user_id:
            return {'success': True, 'message': 'User registered successfully', 'user_id': user_id}
        else:
            return {'success': False, 'message': 'Failed to register user'}
    
    def login_user(self, username, password):
        """Authenticate user login"""
        if not username or not password:
            return None
        
        # Find user by username
        user = self.db.find_user_by_username(username)
        if not user:
            return None
        
        # Check if user is active
        if not user.get('is_active', True):
            return None
        
        # Verify password
        if self.verify_password(user['password'], password):
            # Update last login
            self.db.update_user(user['_id'], {'last_login': datetime.utcnow()})
            return user
        
        return None
    
    def get_user_by_id(self, user_id):
        """Get user information by ID"""
        return self.db.find_user_by_id(user_id)
    
    def change_password(self, user_id, old_password, new_password):
        """Change user password"""
        user = self.db.find_user_by_id(user_id)
        if not user:
            return {'success': False, 'message': 'User not found'}
        
        # Verify old password
        if not self.verify_password(user['password'], old_password):
            return {'success': False, 'message': 'Current password is incorrect'}
        
        # Validate new password
        is_valid, message = self.validate_password(new_password)
        if not is_valid:
            return {'success': False, 'message': message}
        
        # Update password
        hashed_password = self.hash_password(new_password)
        success = self.db.update_user(user_id, {'password': hashed_password})
        
        if success:
            return {'success': True, 'message': 'Password changed successfully'}
        else:
            return {'success': False, 'message': 'Failed to change password'}