"""
Authors data access object
Handles author-related database operations
"""

from db.connection import db


def get_all_authors(limit=None):
    """Get all authors"""
    query = "SELECT author_id, name FROM Authors ORDER BY name"
    if limit:
        query += f" LIMIT {limit}"
    return db.execute_query(query)


def get_author_by_id(author_id):
    """Get author by ID"""
    query = "SELECT author_id, name FROM Authors WHERE author_id = %s"
    return db.execute_query(query, (author_id,), fetch_one=True)


def get_author_by_name(name):
    """Get author by exact name"""
    query = "SELECT author_id, name FROM Authors WHERE name = %s"
    return db.execute_query(query, (name,), fetch_one=True)


def search_authors(name_pattern):
    """Search authors by name pattern"""
    query = """
        SELECT author_id, name 
        FROM Authors 
        WHERE name LIKE %s 
        ORDER BY name
        LIMIT 100
    """
    return db.execute_query(query, (f"%{name_pattern}%",))


def add_author(name):
    """Add new author"""
    query = "INSERT INTO Authors(name) VALUES (%s)"
    author_id = db.execute_update(query, (name,), return_lastrowid=True)
    return author_id


def get_or_create_author(name):
    """Get existing author or create new one"""
    # Try to find existing
    author = get_author_by_name(name)
    if author:
        return author['author_id']
    
    # Create new
    return add_author(name)


def update_author(author_id, name):
    """Update author name"""
    query = "UPDATE Authors SET name = %s WHERE author_id = %s"
    rows = db.execute_update(query, (name, author_id))
    return rows is not None and rows > 0


def delete_author(author_id):
    """Delete author (will fail if books exist due to FK)"""
    query = "DELETE FROM Authors WHERE author_id = %s"
    rows = db.execute_update(query, (author_id,))
    return rows is not None and rows > 0


def get_author_book_count(author_id):
    """Get number of books by author"""
    query = """
        SELECT COUNT(*) as book_count
        FROM Book_Authors
        WHERE author_id = %s
    """
    result = db.execute_query(query, (author_id,), fetch_one=True)
    return result['book_count'] if result else 0