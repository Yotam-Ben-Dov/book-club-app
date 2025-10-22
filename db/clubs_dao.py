"""
Clubs data access object
Handles book club-related database operations
"""

from db.connection import db


def get_all_clubs(public_only=False, limit=100):
    """Get all clubs with basic info"""
    query = """
        SELECT 
            bc.club_id,
            bc.name,
            bc.description,
            bc.is_public,
            bc.created_by,
            bc.max_members,
            u.username as creator_username,
            COUNT(DISTINCT cm.user_id) as member_count,
            (
                SELECT b.title
                FROM Reading_History rh
                JOIN Books b ON rh.ISBN = b.ISBN
                WHERE rh.club_id = bc.club_id AND rh.end_date IS NULL
                LIMIT 1
            ) as current_book
        FROM Book_Clubs bc
        JOIN Users u ON bc.created_by = u.user_id
        LEFT JOIN Club_Members cm ON bc.club_id = cm.club_id
    """
    
    if public_only:
        query += " WHERE bc.is_public = TRUE"
    
    query += " GROUP BY bc.club_id, bc.name, bc.description, bc.is_public, bc.created_by, bc.max_members, u.username"
    query += " ORDER BY bc.name"
    query += f" LIMIT {limit}"
    
    return db.execute_query(query)


def get_club_by_id(club_id):
    """Get detailed club information"""
    query = """
        SELECT 
            bc.club_id,
            bc.name,
            bc.description,
            bc.is_public,
            bc.created_by,
            bc.max_members,
            u.username as creator_username,
            COUNT(DISTINCT cm.user_id) as member_count
        FROM Book_Clubs bc
        JOIN Users u ON bc.created_by = u.user_id
        LEFT JOIN Club_Members cm ON bc.club_id = cm.club_id
        WHERE bc.club_id = %s
        GROUP BY bc.club_id, bc.name, bc.description, bc.is_public, bc.created_by, bc.max_members, u.username
    """
    return db.execute_query(query, (club_id,), fetch_one=True)


def create_club(name, description, is_public, created_by, max_members=50):
    """
    Create new book club and automatically add creator as admin
    Returns club_id on success
    """
    operations = [
        (
            "INSERT INTO Book_Clubs(name, description, is_public, created_by, max_members) VALUES (%s, %s, %s, %s, %s)",
            (name, description, is_public, created_by, max_members)
        )
    ]
    
    # We need to get the club_id, so we'll do this differently
    query = "INSERT INTO Book_Clubs(name, description, is_public, created_by, max_members) VALUES (%s, %s, %s, %s, %s)"
    club_id = db.execute_update(query, (name, description, is_public, created_by, max_members), return_lastrowid=True)
    
    if club_id:
        # Add creator as admin
        add_club_member(club_id, created_by, 'admin')
    
    return club_id


def update_club(club_id, name=None, description=None, is_public=None, max_members=None):
    """Update club information"""
    updates = []
    params = []
    
    if name is not None:
        updates.append("name = %s")
        params.append(name)
    
    if description is not None:
        updates.append("description = %s")
        params.append(description)
    
    if is_public is not None:
        updates.append("is_public = %s")
        params.append(is_public)
    
    if max_members is not None:
        updates.append("max_members = %s")
        params.append(max_members)
    
    if not updates:
        return False
    
    params.append(club_id)
    query = f"UPDATE Book_Clubs SET {', '.join(updates)} WHERE club_id = %s"
    
    rows = db.execute_update(query, tuple(params))
    return rows is not None and rows > 0


def delete_club(club_id):
    """Delete club (cascades to members, queue, history, discussions)"""
    query = "DELETE FROM Book_Clubs WHERE club_id = %s"
    rows = db.execute_update(query, (club_id,))
    return rows is not None and rows > 0


# ============= CLUB MEMBERS =============

def get_club_members(club_id):
    """Get all members of a club with their roles"""
    query = """
        SELECT 
            cm.user_id,
            cm.role,
            u.username,
            u.location,
            u.birth_year
        FROM Club_Members cm
        JOIN Users u ON cm.user_id = u.user_id
        WHERE cm.club_id = %s
        ORDER BY 
            CASE cm.role
                WHEN 'admin' THEN 1
                WHEN 'moderator' THEN 2
                WHEN 'member' THEN 3
            END,
            u.username
    """
    return db.execute_query(query, (club_id,))


def is_user_in_club(club_id, user_id):
    """Check if user is a member of club"""
    query = "SELECT role FROM Club_Members WHERE club_id = %s AND user_id = %s"
    result = db.execute_query(query, (club_id, user_id), fetch_one=True)
    return result is not None


def get_user_role_in_club(club_id, user_id):
    """Get user's role in club"""
    query = "SELECT role FROM Club_Members WHERE club_id = %s AND user_id = %s"
    result = db.execute_query(query, (club_id, user_id), fetch_one=True)
    return result['role'] if result else None


def add_club_member(club_id, user_id, role='member'):
    """Add member to club"""
    query = "INSERT INTO Club_Members(club_id, user_id, role) VALUES (%s, %s, %s)"
    rows = db.execute_update(query, (club_id, user_id, role))
    return rows is not None and rows > 0


def remove_club_member(club_id, user_id):
    """Remove member from club"""
    query = "DELETE FROM Club_Members WHERE club_id = %s AND user_id = %s"
    rows = db.execute_update(query, (club_id, user_id))
    return rows is not None and rows > 0


def update_member_role(club_id, user_id, new_role):
    """Change member's role in club"""
    query = "UPDATE Club_Members SET role = %s WHERE club_id = %s AND user_id = %s"
    rows = db.execute_update(query, (new_role, club_id, user_id))
    return rows is not None and rows > 0


# ============= READING QUEUE =============

def get_club_reading_queue(club_id):
    """
    Get club's reading queue (Simple Query #2)
    Books ordered by queue position
    """
    query = """
        SELECT 
            rq.queue_id,
            rq.queue_position,
            rq.ISBN,
            b.title,
            GROUP_CONCAT(DISTINCT a.name SEPARATOR ', ') as authors,
            u.username as added_by_username,
            AVG(r.rating) as avg_rating,
            COUNT(DISTINCT r.rating_id) as rating_count
        FROM Reading_Queue rq
        JOIN Books b ON rq.ISBN = b.ISBN
        LEFT JOIN Book_Authors ba ON b.ISBN = ba.ISBN
        LEFT JOIN Authors a ON ba.author_id = a.author_id
        LEFT JOIN Users u ON rq.added_by = u.user_id
        LEFT JOIN Ratings r ON b.ISBN = r.ISBN
        WHERE rq.club_id = %s
        GROUP BY rq.queue_id, rq.queue_position, rq.ISBN, b.title, u.username
        ORDER BY rq.queue_position
    """
    return db.execute_query(query, (club_id,))


def add_to_reading_queue(club_id, isbn, added_by):
    """Add book to end of reading queue"""
    # Get next position
    query = "SELECT MAX(queue_position) as max_pos FROM Reading_Queue WHERE club_id = %s"
    result = db.execute_query(query, (club_id,), fetch_one=True)
    next_position = (result['max_pos'] or 0) + 1
    
    # Insert
    query = "INSERT INTO Reading_Queue(club_id, ISBN, queue_position, added_by) VALUES (%s, %s, %s, %s)"
    rows = db.execute_update(query, (club_id, isbn, next_position, added_by))
    return rows is not None and rows > 0


def remove_from_reading_queue(queue_id):
    """Remove book from reading queue"""
    query = "DELETE FROM Reading_Queue WHERE queue_id = %s"
    rows = db.execute_update(query, (queue_id,))
    return rows is not None and rows > 0


def reorder_queue(club_id, queue_updates):
    """
    Update queue positions
    queue_updates: list of (queue_id, new_position) tuples
    """
    query = "UPDATE Reading_Queue SET queue_position = %s WHERE queue_id = %s"
    params_list = [(pos, qid) for qid, pos in queue_updates]
    rows = db.execute_many(query, params_list)
    return rows is not None


# ============= READING HISTORY =============

def get_club_reading_history(club_id):
    """
    Get club's reading history (Simple Query #3)
    Shows completed books and current book
    """
    query = """
        SELECT 
            rh.history_id,
            rh.ISBN,
            b.title,
            GROUP_CONCAT(DISTINCT a.name SEPARATOR ', ') as authors,
            rh.start_date,
            rh.end_date,
            AVG(r.rating) as avg_rating,
            COUNT(DISTINCT r.rating_id) as rating_count,
            CASE WHEN rh.end_date IS NULL THEN 'Current' ELSE 'Completed' END as status
        FROM Reading_History rh
        JOIN Books b ON rh.ISBN = b.ISBN
        LEFT JOIN Book_Authors ba ON b.ISBN = ba.ISBN
        LEFT JOIN Authors a ON ba.author_id = a.author_id
        LEFT JOIN Ratings r ON b.ISBN = r.ISBN
        WHERE rh.club_id = %s
        GROUP BY rh.history_id, rh.ISBN, b.title, rh.start_date, rh.end_date
        ORDER BY rh.start_date DESC
    """
    return db.execute_query(query, (club_id,))


def get_club_current_book(club_id):
    """Get club's current reading book (end_date IS NULL)"""
    query = """
        SELECT 
            rh.history_id,
            rh.ISBN,
            b.title,
            GROUP_CONCAT(DISTINCT a.name SEPARATOR ', ') as authors,
            rh.start_date
        FROM Reading_History rh
        JOIN Books b ON rh.ISBN = b.ISBN
        LEFT JOIN Book_Authors ba ON b.ISBN = ba.ISBN
        LEFT JOIN Authors a ON ba.author_id = a.author_id
        WHERE rh.club_id = %s AND rh.end_date IS NULL
        GROUP BY rh.history_id, rh.ISBN, b.title, rh.start_date
    """
    return db.execute_query(query, (club_id,), fetch_one=True)


def set_current_book(club_id, isbn, start_date=None):
    """
    Set a new current book for the club
    First completes any existing current book
    """
    operations = []
    
    # Complete current book if exists
    operations.append((
        "UPDATE Reading_History SET end_date = CURDATE() WHERE club_id = %s AND end_date IS NULL",
        (club_id,)
    ))
    
    # Add new current book
    if start_date:
        operations.append((
            "INSERT INTO Reading_History(club_id, ISBN, start_date, end_date) VALUES (%s, %s, %s, NULL)",
            (club_id, isbn, start_date)
        ))
    else:
        operations.append((
            "INSERT INTO Reading_History(club_id, ISBN, start_date, end_date) VALUES (%s, %s, CURDATE(), NULL)",
            (club_id, isbn)
        ))
    
    return db.execute_transaction(operations)


def complete_current_book(club_id, end_date=None):
    """Mark current book as completed"""
    if end_date:
        query = "UPDATE Reading_History SET end_date = %s WHERE club_id = %s AND end_date IS NULL"
        params = (end_date, club_id)
    else:
        query = "UPDATE Reading_History SET end_date = CURDATE() WHERE club_id = %s AND end_date IS NULL"
        params = (club_id,)
    
    rows = db.execute_update(query, params)
    return rows is not None and rows > 0


# ============= DISCUSSIONS =============

def get_club_recent_discussions(club_id, limit=20):
    """
    Get recent discussions from club (Simple Query #4)
    Combines general and chapter discussions
    """
    query = """
        (
            SELECT 
                gd.discussion_id,
                'general' as discussion_type,
                gd.title,
                gd.content,
                NULL as ISBN,
                NULL as chapter_number,
                u.username,
                gd.created_date
            FROM General_Discussions gd
            JOIN Users u ON gd.user_id = u.user_id
            WHERE gd.club_id = %s
        )
        UNION ALL
        (
            SELECT 
                cd.discussion_id,
                'chapter' as discussion_type,
                cd.title,
                cd.content,
                cd.ISBN,
                cd.chapter_number,
                u.username,
                cd.created_date
            FROM Chapter_Discussions cd
            JOIN Users u ON cd.user_id = u.user_id
            WHERE cd.club_id = %s
        )
        ORDER BY created_date DESC
        LIMIT %s
    """
    return db.execute_query(query, (club_id, club_id, limit))


def add_general_discussion(club_id, user_id, title, content):
    """Add general discussion to club"""
    query = """
        INSERT INTO General_Discussions(club_id, user_id, title, content)
        VALUES (%s, %s, %s, %s)
    """
    discussion_id = db.execute_update(query, (club_id, user_id, title, content), return_lastrowid=True)
    return discussion_id


def add_chapter_discussion(club_id, isbn, chapter_number, user_id, title, content):
    """Add chapter-specific discussion"""
    query = """
        INSERT INTO Chapter_Discussions(club_id, ISBN, chapter_number, user_id, title, content)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    discussion_id = db.execute_update(query, (club_id, isbn, chapter_number, user_id, title, content), return_lastrowid=True)
    return discussion_id


def delete_general_discussion(discussion_id):
    """Delete general discussion"""
    query = "DELETE FROM General_Discussions WHERE discussion_id = %s"
    rows = db.execute_update(query, (discussion_id,))
    return rows is not None and rows > 0


def delete_chapter_discussion(discussion_id):
    """Delete chapter discussion"""
    query = "DELETE FROM Chapter_Discussions WHERE discussion_id = %s"
    rows = db.execute_update(query, (discussion_id,))
    return rows is not None and rows > 0


def get_user_clubs(user_id):
    """Get all clubs a user is member of"""
    query = """
        SELECT 
            bc.club_id,
            bc.name,
            bc.description,
            bc.is_public,
            cm.role
        FROM Club_Members cm
        JOIN Book_Clubs bc ON cm.club_id = bc.club_id
        WHERE cm.user_id = %s
        ORDER BY bc.name
    """
    return db.execute_query(query, (user_id,))