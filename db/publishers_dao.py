"""
Publishers data access object
Handles publisher-related database operations
"""

from db.connection import db


def get_all_publishers(limit=None):
    """Get all publishers"""
    query = "SELECT publisher_id, name FROM Publishers ORDER BY name"
    if limit:
        query += f" LIMIT {limit}"
    return db.execute_query(query)


def get_publisher_by_id(publisher_id):
    """Get publisher by ID"""
    query = "SELECT publisher_id, name FROM Publishers WHERE publisher_id = %s"
    return db.execute_query(query, (publisher_id,), fetch_one=True)


def get_publisher_by_name(name):
    """Get publisher by exact name"""
    query = "SELECT publisher_id, name FROM Publishers WHERE name = %s"
    return db.execute_query(query, (name,), fetch_one=True)


def search_publishers(name_pattern):
    """Search publishers by name pattern"""
    query = """
        SELECT publisher_id, name 
        FROM Publishers 
        WHERE name LIKE %s 
        ORDER BY name
        LIMIT 100
    """
    return db.execute_query(query, (f"%{name_pattern}%",))


def add_publisher(name):
    """Add new publisher"""
    query = "INSERT INTO Publishers(name) VALUES (%s)"
    publisher_id = db.execute_update(query, (name,), return_lastrowid=True)
    return publisher_id


def get_or_create_publisher(name):
    """Get existing publisher or create new one"""
    if not name:
        return None
    
    # Try to find existing
    publisher = get_publisher_by_name(name)
    if publisher:
        return publisher['publisher_id']
    
    # Create new
    return add_publisher(name)


def update_publisher(publisher_id, name):
    """Update publisher name"""
    query = "UPDATE Publishers SET name = %s WHERE publisher_id = %s"
    rows = db.execute_update(query, (name, publisher_id))
    return rows is not None and rows > 0


def delete_publisher(publisher_id):
    """Delete publisher (will set books.publisher_id to NULL due to FK)"""
    query = "DELETE FROM Publishers WHERE publisher_id = %s"
    rows = db.execute_update(query, (publisher_id,))
    return rows is not None and rows > 0