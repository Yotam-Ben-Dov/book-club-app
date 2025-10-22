"""
Input validation functions
Used by UI layer to validate user input before sending to database
"""

import re
from datetime import datetime
from config import MIN_YEAR, MAX_YEAR


def validate_isbn(isbn):
    """
    Validate ISBN format
    Returns: (is_valid, error_message)
    """
    if not isbn:
        return False, "ISBN cannot be empty"
    
    # Remove hyphens and spaces
    isbn_clean = isbn.replace('-', '').replace(' ', '')
    
    # Check if it's numeric
    if not isbn_clean.isdigit():
        return False, "ISBN must contain only digits (and optional hyphens)"
    
    # Check length (ISBN-10 or ISBN-13)
    if len(isbn_clean) not in [10, 13]:
        return False, f"ISBN must be 10 or 13 digits (got {len(isbn_clean)})"
    
    return True, ""


def validate_year(year):
    """
    Validate publication year
    Returns: (is_valid, error_message)
    """
    if year is None or year == '':
        return True, ""  # Optional field
    
    try:
        year_int = int(year)
        if year_int < MIN_YEAR or year_int > MAX_YEAR:
            return False, f"Year must be between {MIN_YEAR} and {MAX_YEAR}"
        return True, ""
    except ValueError:
        return False, "Year must be a valid number"


def validate_rating(rating):
    """
    Validate book rating (0-10)
    Returns: (is_valid, error_message)
    """
    if rating is None or rating == '':
        return False, "Rating cannot be empty"
    
    try:
        rating_int = int(rating)
        if rating_int < 0 or rating_int > 10:
            return False, "Rating must be between 0 and 10"
        return True, ""
    except ValueError:
        return False, "Rating must be a valid number"


def validate_username(username):
    """
    Validate username
    Returns: (is_valid, error_message)
    """
    if not username:
        return False, "Username cannot be empty"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 50:
        return False, "Username cannot exceed 50 characters"
    
    # Allow alphanumeric and underscores
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    
    return True, ""


def validate_password(password):
    """
    Validate password
    Returns: (is_valid, error_message)
    """
    if not password:
        return False, "Password cannot be empty"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    if len(password) > 255:
        return False, "Password cannot exceed 255 characters"
    
    return True, ""


def validate_user_id(user_id):
    """
    Validate user ID
    Returns: (is_valid, error_message)
    """
    if user_id is None or user_id == '':
        return False, "User ID cannot be empty"
    
    try:
        user_id_int = int(user_id)
        if user_id_int <= 0:
            return False, "User ID must be positive"
        return True, ""
    except ValueError:
        return False, "User ID must be a valid number"


def validate_location(location):
    """
    Validate location string
    Returns: (is_valid, error_message)
    """
    if not location:
        return False, "Location cannot be empty"
    
    if len(location) < 2:
        return False, "Location must be at least 2 characters"
    
    if len(location) > 255:
        return False, "Location cannot exceed 255 characters"
    
    return True, ""


def validate_birth_year(birth_year):
    """
    Validate birth year
    Returns: (is_valid, error_message)
    """
    if birth_year is None or birth_year == '':
        return False, "Birth year cannot be empty"
    
    try:
        year_int = int(birth_year)
        current_year = datetime.now().year
        
        if year_int < 1900:
            return False, "Birth year cannot be before 1900"
        
        if year_int > current_year:
            return False, "Birth year cannot be in the future"
        
        age = current_year - year_int
        if age < 6:
            return False, "User must be at least 6 years old"
        
        if age > 120:
            return False, "Birth year seems invalid (age > 120)"
        
        return True, ""
    except ValueError:
        return False, "Birth year must be a valid number"


def validate_title(title):
    """
    Validate book title
    Returns: (is_valid, error_message)
    """
    if not title:
        return False, "Title cannot be empty"
    
    if len(title) < 1:
        return False, "Title must be at least 1 character"
    
    if len(title) > 255:
        return False, "Title cannot exceed 255 characters"
    
    return True, ""


def validate_name(name, field_name="Name"):
    """
    Validate author/publisher name
    Returns: (is_valid, error_message)
    """
    if not name:
        return False, f"{field_name} cannot be empty"
    
    if len(name) < 1:
        return False, f"{field_name} must be at least 1 character"
    
    if len(name) > 255:
        return False, f"{field_name} cannot exceed 255 characters"
    
    return True, ""


def validate_club_name(name):
    """
    Validate club name
    Returns: (is_valid, error_message)
    """
    if not name:
        return False, "Club name cannot be empty"
    
    if len(name) < 3:
        return False, "Club name must be at least 3 characters"
    
    if len(name) > 255:
        return False, "Club name cannot exceed 255 characters"
    
    return True, ""


def validate_max_members(max_members):
    """
    Validate max members for club
    Returns: (is_valid, error_message)
    """
    if max_members is None or max_members == '':
        return True, ""  # Optional, will use default
    
    try:
        max_int = int(max_members)
        if max_int < 2:
            return False, "Max members must be at least 2"
        if max_int > 1000:
            return False, "Max members cannot exceed 1000"
        return True, ""
    except ValueError:
        return False, "Max members must be a valid number"


def validate_chapter_number(chapter):
    """
    Validate chapter number
    Returns: (is_valid, error_message)
    """
    if chapter is None or chapter == '':
        return False, "Chapter number cannot be empty"
    
    try:
        chapter_int = int(chapter)
        if chapter_int < 1:
            return False, "Chapter number must be at least 1"
        if chapter_int > 500:
            return False, "Chapter number cannot exceed 500"
        return True, ""
    except ValueError:
        return False, "Chapter number must be a valid number"