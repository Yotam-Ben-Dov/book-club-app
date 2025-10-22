"""
Users data access object
Handles user-related database operations
"""

from db.connection import db


def search_users(username=None, location=None, min_birth_year=None, max_birth_year=None, limit=100):
    """Search users with filters"""
    query = """
        SELECT user_id, username, location, birth_year
        FROM Users
        WHERE 1=1
    """
    
    params = []
    
    if username:
        query += " AND username LIKE %s"
        params.append(f"%{username}%")
    
    if location:
        query += " AND location LIKE %s"
        params.append(f"%{location}%")
    
    if min_birth_year:
        query += " AND birth_year >= %s"
        params.append(min_birth_year)
    
    if max_birth_year:
        query += " AND birth_year <= %s"
        params.append(max_birth_year)
    
    query += " ORDER BY username"
    query += f" LIMIT {limit}"
    
    return db.execute_query(query, tuple(params))


def get_user_by_id(user_id):
    """Get user by ID"""
    query = "SELECT user_id, username, location, birth_year FROM Users WHERE user_id = %s"
    return db.execute_query(query, (user_id,), fetch_one=True)


def get_user_by_username(username):
    """Get user by username"""
    query = "SELECT user_id, username, password, location, birth_year FROM Users WHERE username = %s"
    return db.execute_query(query, (username,), fetch_one=True)


def add_user(user_id, username, password, location, birth_year):
    """Add new user with specific ID"""
    query = """
        INSERT INTO Users(user_id, username, password, location, birth_year)
        VALUES (%s, %s, %s, %s, %s)
    """
    rows = db.execute_update(query, (user_id, username, password, location, birth_year))
    return rows is not None and rows > 0


def update_user(user_id, username=None, password=None, location=None, birth_year=None):
    """Update user information"""
    updates = []
    params = []
    
    if username is not None:
        updates.append("username = %s")
        params.append(username)
    
    if password is not None:
        updates.append("password = %s")
        params.append(password)
    
    if location is not None:
        updates.append("location = %s")
        params.append(location)
    
    if birth_year is not None:
        updates.append("birth_year = %s")
        params.append(birth_year)
    
    if not updates:
        return False
    
    params.append(user_id)
    query = f"UPDATE Users SET {', '.join(updates)} WHERE user_id = %s"
    
    rows = db.execute_update(query, tuple(params))
    return rows is not None and rows > 0


def delete_user(user_id):
    """Delete user (cascades to ratings, club memberships, etc.)"""
    query = "DELETE FROM Users WHERE user_id = %s"
    rows = db.execute_update(query, (user_id,))
    return rows is not None and rows > 0


def get_user_reading_statistics(user_id):
    """
    Get user reading statistics
    
    Returns:
        - Total books rated
        - Average rating given
        - Favorite author (most rated)
        - Reading diversity (unique authors rated)
    """
    query = """
        SELECT 
            u.user_id,
            u.username,
            COUNT(DISTINCT r.ISBN) as books_rated,
            AVG(r.rating) as avg_rating_given,
            COUNT(DISTINCT ba.author_id) as unique_authors_rated,
            (
                SELECT a.name
                FROM Ratings r2
                JOIN Book_Authors ba2 ON r2.ISBN = ba2.ISBN
                JOIN Authors a ON ba2.author_id = a.author_id
                WHERE r2.user_id = u.user_id
                GROUP BY a.author_id, a.name
                ORDER BY COUNT(*) DESC
                LIMIT 1
            ) as favorite_author
        FROM Users u
        LEFT JOIN Ratings r ON u.user_id = r.user_id
        LEFT JOIN Book_Authors ba ON r.ISBN = ba.ISBN
        WHERE u.user_id = %s
        GROUP BY u.user_id, u.username
    """
    return db.execute_query(query, (user_id,), fetch_one=True)


def get_all_users_count():
    """Get total number of users"""
    query = "SELECT COUNT(*) as count FROM Users"
    result = db.execute_query(query, fetch_one=True)
    return result['count'] if result else 0


def get_next_user_id():
    """Get next available user ID"""
    query = "SELECT MAX(user_id) as max_id FROM Users"
    result = db.execute_query(query, fetch_one=True)
    return (result['max_id'] or 0) + 1 if result else 1