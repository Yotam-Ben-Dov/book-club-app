"""
Simple queries data access object
Contains 10 simple analytical queries
"""

from db.connection import db


def get_books_trending_in_clubs(limit=20):
    """
    Books trending in clubs
    Books most frequently added to reading queues
    """
    query = """
        SELECT 
            b.ISBN,
            b.title,
            GROUP_CONCAT(DISTINCT a.name SEPARATOR ', ') as authors,
            p.name as publisher,
            COUNT(DISTINCT rq.club_id) as clubs_count,
            AVG(r.rating) as avg_rating,
            COUNT(DISTINCT r.rating_id) as rating_count
        FROM Books b
        JOIN Reading_Queue rq ON b.ISBN = rq.ISBN
        LEFT JOIN Book_Authors ba ON b.ISBN = ba.ISBN
        LEFT JOIN Authors a ON ba.author_id = a.author_id
        LEFT JOIN Publishers p ON b.publisher_id = p.publisher_id
        LEFT JOIN Ratings r ON b.ISBN = r.ISBN
        GROUP BY b.ISBN, b.title, p.name
        HAVING clubs_count > 0
        ORDER BY clubs_count DESC, avg_rating DESC
        LIMIT %s
    """
    return db.execute_query(query, (limit,))


def get_most_discussed_books(limit=20):
    """
    Most discussed books
    Books with most chapter discussions across all clubs
    """
    query = """
        SELECT 
            b.ISBN,
            b.title,
            GROUP_CONCAT(DISTINCT a.name SEPARATOR ', ') as authors,
            COUNT(DISTINCT cd.discussion_id) as discussion_count,
            COUNT(DISTINCT cd.club_id) as clubs_discussing,
            AVG(r.rating) as avg_rating
        FROM Books b
        JOIN Chapter_Discussions cd ON b.ISBN = cd.ISBN
        LEFT JOIN Book_Authors ba ON b.ISBN = ba.ISBN
        LEFT JOIN Authors a ON ba.author_id = a.author_id
        LEFT JOIN Ratings r ON b.ISBN = r.ISBN
        GROUP BY b.ISBN, b.title
        ORDER BY discussion_count DESC, clubs_discussing DESC
        LIMIT %s
    """
    return db.execute_query(query, (limit,))

def get_publisher_comparison():
    """
    Publisher comparison
    Publishers ranked by book count, average ratings, and club selections
    """
    query = """
        SELECT 
            p.publisher_id,
            p.name as publisher_name,
            COUNT(DISTINCT b.ISBN) as total_books,
            AVG(r.rating) as avg_rating,
            COUNT(DISTINCT r.rating_id) as total_ratings,
            COUNT(DISTINCT rh.club_id) as club_selections
        FROM Publishers p
        LEFT JOIN Books b ON p.publisher_id = b.publisher_id
        LEFT JOIN Ratings r ON b.ISBN = r.ISBN
        LEFT JOIN Reading_History rh ON b.ISBN = rh.ISBN
        GROUP BY p.publisher_id, p.name
        HAVING total_books > 0
        ORDER BY total_books DESC, avg_rating DESC
        LIMIT 50
    """
    return db.execute_query(query)


def get_most_prolific_authors(limit=20):
    """
    Most prolific authors
    Authors ranked by number of books and average ratings
    """
    query = """
        SELECT 
            a.author_id,
            a.name as author_name,
            COUNT(DISTINCT ba.ISBN) as book_count,
            AVG(r.rating) as avg_rating,
            COUNT(DISTINCT r.rating_id) as total_ratings,
            GROUP_CONCAT(DISTINCT b.title ORDER BY b.title SEPARATOR ' | ') as sample_books
        FROM Authors a
        JOIN Book_Authors ba ON a.author_id = ba.author_id
        LEFT JOIN Books b ON ba.ISBN = b.ISBN
        LEFT JOIN Ratings r ON b.ISBN = r.ISBN
        GROUP BY a.author_id, a.name
        HAVING book_count > 0
        ORDER BY book_count DESC, avg_rating DESC
        LIMIT %s
    """
    return db.execute_query(query, (limit,))


def get_location_based_stats():
    """
    Location-based statistics
    User distribution and popular books by location/region
    """
    query = """
        SELECT 
            u.location,
            COUNT(DISTINCT u.user_id) as user_count,
            COUNT(DISTINCT r.rating_id) as total_ratings,
            AVG(r.rating) as avg_rating_given,
            (
                SELECT b.title
                FROM Ratings r2
                JOIN Books b ON r2.ISBN = b.ISBN
                JOIN Users u2 ON r2.user_id = u2.user_id
                WHERE u2.location = u.location
                GROUP BY b.ISBN, b.title
                ORDER BY AVG(r2.rating) DESC, COUNT(*) DESC
                LIMIT 1
            ) as most_popular_book
        FROM Users u
        LEFT JOIN Ratings r ON u.user_id = r.user_id
        GROUP BY u.location
        HAVING user_count >= 5
        ORDER BY user_count DESC
        LIMIT 30
    """
    return db.execute_query(query)


def get_top_rated_books(min_ratings=10, limit=50):
    """
    Get top-rated books with minimum rating threshold
    """
    query = """
        SELECT 
            b.ISBN,
            b.title,
            GROUP_CONCAT(DISTINCT a.name SEPARATOR ', ') as authors,
            p.name as publisher,
            b.year_of_publication,
            AVG(r.rating) as avg_rating,
            COUNT(r.rating_id) as rating_count
        FROM Books b
        LEFT JOIN Book_Authors ba ON b.ISBN = ba.ISBN
        LEFT JOIN Authors a ON ba.author_id = a.author_id
        LEFT JOIN Publishers p ON b.publisher_id = p.publisher_id
        LEFT JOIN Ratings r ON b.ISBN = r.ISBN
        GROUP BY b.ISBN, b.title, p.name, b.year_of_publication
        HAVING rating_count >= %s
        ORDER BY avg_rating DESC, rating_count DESC
        LIMIT %s
    """
    return db.execute_query(query, (min_ratings, limit))


def get_club_activity_metrics():
    """
    Get activity metrics for all clubs
    """
    query = """
        SELECT 
            bc.club_id,
            bc.name as club_name,
            COUNT(DISTINCT cm.user_id) as member_count,
            COUNT(DISTINCT gd.discussion_id) + COUNT(DISTINCT cd.discussion_id) as total_discussions,
            COUNT(DISTINCT rh.history_id) as books_completed,
            COUNT(DISTINCT rq.queue_id) as books_in_queue
        FROM Book_Clubs bc
        LEFT JOIN Club_Members cm ON bc.club_id = cm.club_id
        LEFT JOIN General_Discussions gd ON bc.club_id = gd.club_id
        LEFT JOIN Chapter_Discussions cd ON bc.club_id = cd.club_id
        LEFT JOIN Reading_History rh ON bc.club_id = rh.club_id AND rh.end_date IS NOT NULL
        LEFT JOIN Reading_Queue rq ON bc.club_id = rq.club_id
        GROUP BY bc.club_id, bc.name
        ORDER BY total_discussions DESC, member_count DESC
    """
    return db.execute_query(query)


def get_inactive_users(days=90):
    """
    Find users with no ratings in the last N days
    (Using rating_id as proxy for activity date since Ratings table doesn't have timestamp)
    """
    query = """
        SELECT 
            u.user_id,
            u.username,
            u.location,
            COUNT(r.rating_id) as total_ratings,
            COUNT(DISTINCT cm.club_id) as clubs_joined
        FROM Users u
        LEFT JOIN Ratings r ON u.user_id = r.user_id
        LEFT JOIN Club_Members cm ON u.user_id = cm.user_id
        GROUP BY u.user_id, u.username, u.location
        HAVING total_ratings = 0 OR clubs_joined = 0
        ORDER BY u.user_id
        LIMIT 100
    """
    return db.execute_query(query)


def get_rating_distribution_for_book(isbn):
    """
    Get rating distribution (1-10) for a specific book
    """
    query = """
        SELECT 
            r.rating,
            COUNT(*) as count
        FROM Ratings r
        WHERE r.ISBN = %s
        GROUP BY r.rating
        ORDER BY r.rating
    """
    return db.execute_query(query, (isbn,))


def get_books_by_year_range(start_year, end_year, limit=100):
    """
    Get books published in a year range
    """
    query = """
        SELECT 
            b.ISBN,
            b.title,
            b.year_of_publication,
            GROUP_CONCAT(DISTINCT a.name SEPARATOR ', ') as authors,
            p.name as publisher,
            AVG(r.rating) as avg_rating,
            COUNT(DISTINCT r.rating_id) as rating_count
        FROM Books b
        LEFT JOIN Book_Authors ba ON b.ISBN = ba.ISBN
        LEFT JOIN Authors a ON ba.author_id = a.author_id
        LEFT JOIN Publishers p ON b.publisher_id = p.publisher_id
        LEFT JOIN Ratings r ON b.ISBN = r.ISBN
        WHERE b.year_of_publication BETWEEN %s AND %s
        GROUP BY b.ISBN, b.title, b.year_of_publication, p.name
        ORDER BY b.year_of_publication DESC, avg_rating DESC
        LIMIT %s
    """
    return db.execute_query(query, (start_year, end_year, limit))


def search_discussions(search_term, club_id=None, limit=50):
    """
    Search discussions by title or content
    """
    query = """
        (
            SELECT 
                gd.discussion_id,
                'general' as type,
                gd.club_id,
                bc.name as club_name,
                gd.title,
                gd.content,
                u.username,
                gd.created_date
            FROM General_Discussions gd
            JOIN Book_Clubs bc ON gd.club_id = bc.club_id
            JOIN Users u ON gd.user_id = u.user_id
            WHERE (gd.title LIKE %s OR gd.content LIKE %s)
    """
    
    params = [f"%{search_term}%", f"%{search_term}%"]
    
    if club_id:
        query += " AND gd.club_id = %s"
        params.append(club_id)
    
    query += """
        )
        UNION ALL
        (
            SELECT 
                cd.discussion_id,
                'chapter' as type,
                cd.club_id,
                bc.name as club_name,
                cd.title,
                cd.content,
                u.username,
                cd.created_date
            FROM Chapter_Discussions cd
            JOIN Book_Clubs bc ON cd.club_id = bc.club_id
            JOIN Users u ON cd.user_id = u.user_id
            WHERE (cd.title LIKE %s OR cd.content LIKE %s)
    """
    
    params.extend([f"%{search_term}%", f"%{search_term}%"])
    
    if club_id:
        query += " AND cd.club_id = %s"
        params.append(club_id)
    
    query += f"""
        )
        ORDER BY created_date DESC
        LIMIT {limit}
    """
    
    return db.execute_query(query, tuple(params))