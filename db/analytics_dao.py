"""
Analytics data access object
Contains 3 complex analytical queries
"""

from db.connection import db


def get_top_publishers_by_rating(min_books=5, min_ratings=50):
    """
    COMPLEX QUERY 1: Top Publishers by Average Rating and Number of Books
    
    Analyzes publishers based on:
    - Total books published
    - Average rating across all their books
    - Total number of ratings received
    - Minimum thresholds for reliability
    
    Uses: Multiple JOINs, GROUP BY, aggregations (COUNT DISTINCT, AVG), 
          HAVING with compound conditions, ORDER BY
    """
    query = """
        SELECT 
            p.name AS publisher_name,
            COUNT(DISTINCT b.ISBN) AS total_books,
            ROUND(AVG(r.rating), 2) AS avg_rating,
            COUNT(r.rating_id) AS total_ratings
        FROM Publishers p
        JOIN Books b ON p.publisher_id = b.publisher_id
        JOIN Ratings r ON b.ISBN = r.ISBN
        GROUP BY p.publisher_id, p.name
        HAVING COUNT(DISTINCT b.ISBN) >= %s 
           AND COUNT(r.rating_id) >= %s
        ORDER BY avg_rating DESC, total_ratings DESC
        LIMIT 20
    """
    return db.execute_query(query, (min_books, min_ratings))


def get_top_rated_books_by_age_group(min_ratings=10, book_search=None):
    """
    COMPLEX QUERY 2: Top Rated Books by Age Group
    
    Analyzes reading preferences across different generations:
    - Gen Z (18-25)
    - Millennials (26-40)
    - Gen X (41-55)
    - Boomers+ (56+)
    
    Shows which books are most popular in each age group
    Optional: Filter by book title or ISBN
    
    Uses: CASE statements for age grouping, JOINs (3 tables), 
          GROUP BY on computed column, aggregations (COUNT, AVG), HAVING,
          optional WHERE clause for book filtering
    """
    query = """
        SELECT 
            CASE 
                WHEN YEAR(CURDATE()) - u.birth_year <= 25 THEN 'Gen Z (18-25)'
                WHEN YEAR(CURDATE()) - u.birth_year <= 40 THEN 'Millennials (26-40)'
                WHEN YEAR(CURDATE()) - u.birth_year <= 55 THEN 'Gen X (41-55)'
                ELSE 'Boomers+ (56+)'
            END AS age_group,
            b.ISBN,
            b.title,
            COUNT(r.rating_id) AS num_ratings,
            ROUND(AVG(r.rating), 2) AS avg_rating
        FROM Users u
        JOIN Ratings r ON u.user_id = r.user_id
        JOIN Books b ON r.ISBN = b.ISBN
    """
    
    params = []
    
    # Add WHERE clause if searching for specific book
    if book_search:
        query += " WHERE (b.title LIKE %s OR b.ISBN LIKE %s)"
        search_param = f"%{book_search}%"
        params.extend([search_param, search_param])
    
    query += """
        GROUP BY age_group, b.ISBN, b.title
        HAVING num_ratings >= %s
        ORDER BY age_group, avg_rating DESC, num_ratings DESC
    """
    
    params.append(min_ratings)
    
    return db.execute_query(query, tuple(params))

def get_most_active_book_clubs(min_members=3):
    """
    COMPLEX QUERY 3: Most Active Book Clubs with Engagement Metrics
    
    Analyzes club activity and engagement:
    - Member count
    - Books read (from history)
    - Total discussions started
    - Total comments on discussions
    - Discussions per member (engagement ratio)
    
    Uses: Multiple JOINs (5 tables), GROUP BY, multiple COUNT(DISTINCT) aggregations,
          complex calculation with NULLIF, HAVING, ORDER BY on calculated field
    """
    query = """
        SELECT 
            bc.club_id,
            bc.name AS club_name,
            COUNT(DISTINCT cm.user_id) AS member_count,
            COUNT(DISTINCT rh.ISBN) AS books_read,
            COUNT(DISTINCT gd.discussion_id) AS total_discussions,
            COUNT(DISTINCT gdc.comment_id) AS total_comments,
            ROUND(COUNT(DISTINCT gd.discussion_id) / 
                  NULLIF(COUNT(DISTINCT cm.user_id), 0), 2) AS discussions_per_member
        FROM Book_Clubs bc
        LEFT JOIN Club_Members cm ON bc.club_id = cm.club_id
        LEFT JOIN Reading_History rh ON bc.club_id = rh.club_id
        LEFT JOIN General_Discussions gd ON bc.club_id = gd.club_id
        LEFT JOIN General_Discussion_Comments gdc ON gd.discussion_id = gdc.discussion_id
        GROUP BY bc.club_id, bc.name
        HAVING member_count >= %s
        ORDER BY discussions_per_member DESC, total_discussions DESC
        LIMIT 20
    """
    return db.execute_query(query, (min_members,))