"""
Ratings data access object
Handles rating-related database operations
"""

from db.connection import db


def get_ratings(user_id=None, isbn=None, min_rating=None, limit=100):
    """Get ratings with optional filters"""
    query = """
        SELECT 
            r.rating_id,
            r.user_id,
            r.ISBN,
            r.rating,
            u.username,
            b.title as book_title,
            GROUP_CONCAT(DISTINCT a.name SEPARATOR ', ') as authors
        FROM Ratings r
        JOIN Users u ON r.user_id = u.user_id
        JOIN Books b ON r.ISBN = b.ISBN
        LEFT JOIN Book_Authors ba ON b.ISBN = ba.ISBN
        LEFT JOIN Authors a ON ba.author_id = a.author_id
        WHERE 1=1
    """
    
    params = []
    
    if user_id:
        query += " AND r.user_id = %s"
        params.append(user_id)
    
    if isbn:
        query += " AND r.ISBN = %s"
        params.append(isbn)
    
    if min_rating:
        query += " AND r.rating >= %s"
        params.append(min_rating)
    
    query += " GROUP BY r.rating_id, r.user_id, r.ISBN, r.rating, u.username, b.title"
    query += " ORDER BY r.rating_id DESC"
    query += f" LIMIT {limit}"
    
    return db.execute_query(query, tuple(params))


def get_rating_by_id(rating_id):
    """Get specific rating by ID"""
    query = """
        SELECT 
            r.rating_id,
            r.user_id,
            r.ISBN,
            r.rating,
            u.username,
            b.title as book_title
        FROM Ratings r
        JOIN Users u ON r.user_id = u.user_id
        JOIN Books b ON r.ISBN = b.ISBN
        WHERE r.rating_id = %s
    """
    return db.execute_query(query, (rating_id,), fetch_one=True)


def get_user_book_rating(user_id, isbn):
    """Check if user has rated a specific book"""
    query = """
        SELECT rating_id, rating
        FROM Ratings
        WHERE user_id = %s AND ISBN = %s
    """
    return db.execute_query(query, (user_id, isbn), fetch_one=True)


def add_rating(user_id, isbn, rating):
    """Add new rating (or update if exists due to UNIQUE constraint)"""
    query = """
        INSERT INTO Ratings(user_id, ISBN, rating)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE rating = %s
    """
    rows = db.execute_update(query, (user_id, isbn, rating, rating))
    return rows is not None and rows > 0


def update_rating(rating_id, new_rating):
    """Update existing rating"""
    query = "UPDATE Ratings SET rating = %s WHERE rating_id = %s"
    rows = db.execute_update(query, (new_rating, rating_id))
    return rows is not None and rows > 0


def delete_rating(rating_id):
    """Delete rating"""
    query = "DELETE FROM Ratings WHERE rating_id = %s"
    rows = db.execute_update(query, (rating_id,))
    return rows is not None and rows > 0


def delete_user_book_rating(user_id, isbn):
    """Delete specific user's rating for a book"""
    query = "DELETE FROM Ratings WHERE user_id = %s AND ISBN = %s"
    rows = db.execute_update(query, (user_id, isbn))
    return rows is not None and rows > 0


def get_book_ratings_summary(isbn):
    """Get rating statistics for a book"""
    query = """
        SELECT 
            COUNT(*) as rating_count,
            AVG(rating) as avg_rating,
            MIN(rating) as min_rating,
            MAX(rating) as max_rating,
            SUM(CASE WHEN rating >= 8 THEN 1 ELSE 0 END) as high_ratings,
            SUM(CASE WHEN rating >= 5 AND rating < 8 THEN 1 ELSE 0 END) as medium_ratings,
            SUM(CASE WHEN rating < 5 THEN 1 ELSE 0 END) as low_ratings
        FROM Ratings
        WHERE ISBN = %s
    """
    return db.execute_query(query, (isbn,), fetch_one=True)


def get_user_ratings_summary(user_id):
    """Get rating statistics for a user"""
    query = """
        SELECT 
            COUNT(*) as rating_count,
            AVG(rating) as avg_rating,
            MIN(rating) as min_rating,
            MAX(rating) as max_rating
        FROM Ratings
        WHERE user_id = %s
    """
    return db.execute_query(query, (user_id,), fetch_one=True)