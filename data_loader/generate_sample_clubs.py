import mysql.connector
import random
from datetime import datetime, timedelta
from config import DB_CONFIG


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def get_random_users(cursor, count):
    """Get random user IDs"""
    cursor.execute(f"SELECT user_id FROM Users ORDER BY RAND() LIMIT {count}")
    return [row[0] for row in cursor.fetchall()]


def get_random_books(cursor, count):
    """Get random ISBNs"""
    cursor.execute(f"SELECT ISBN FROM Books ORDER BY RAND() LIMIT {count}")
    return [row[0] for row in cursor.fetchall()]


def create_club(cursor, name, description, is_public, creator_id):
    """Create a book club and return its ID"""
    sql = """INSERT INTO Book_Clubs(name, description, is_public, created_by) 
             VALUES (%s, %s, %s, %s)"""
    cursor.execute(sql, (name, description, is_public, creator_id))
    return cursor.lastrowid


def add_club_member(cursor, club_id, user_id, role='member'):
    """Add a member to a club"""
    sql = "INSERT INTO Club_Members(club_id, user_id, role) VALUES (%s, %s, %s)"
    try:
        cursor.execute(sql, (club_id, user_id, role))
    except:
        pass  # Member might already exist


def set_current_book(cursor, club_id, isbn):
    sql = """INSERT INTO Reading_History(club_id, ISBN, start_date, end_date) 
             VALUES (%s, %s, CURDATE(), NULL)"""
    try:
        cursor.execute(sql, (club_id, isbn))
    except:
        pass


def add_to_queue(cursor, club_id, isbn, position, added_by):
    """Add a book to reading queue"""
    sql = """INSERT INTO Reading_Queue(club_id, ISBN, queue_position, added_by) 
             VALUES (%s, %s, %s, %s)"""
    try:
        cursor.execute(sql, (club_id, isbn, position, added_by))
    except:
        pass  # Book might already be in queue


def add_to_history(cursor, club_id, isbn):
    """Add a completed book to reading history (with end_date)"""
    # Random dates in the past
    end_days_ago = random.randint(10, 90)
    start_days_ago = end_days_ago + random.randint(14, 44)
    
    end_date = datetime.now() - timedelta(days=end_days_ago)
    start_date = datetime.now() - timedelta(days=start_days_ago)
    
    sql = """INSERT INTO Reading_History(club_id, ISBN, start_date, end_date) 
             VALUES (%s, %s, %s, %s)"""
    try:
        cursor.execute(sql, (club_id, isbn, start_date.date(), end_date.date()))
    except:
        pass


def create_general_discussion(cursor, club_id, user_id, title, content):
    """Create a general discussion"""
    sql = """INSERT INTO General_Discussions(club_id, user_id, title, content) 
             VALUES (%s, %s, %s, %s)"""
    cursor.execute(sql, (club_id, user_id, title, content))


def create_chapter_discussion(cursor, club_id, isbn, chapter, user_id, title, content):
    """Create a chapter discussion"""
    sql = """INSERT INTO Chapter_Discussions(club_id, ISBN, chapter_number, user_id, title, content) 
             VALUES (%s, %s, %s, %s, %s, %s)"""
    cursor.execute(sql, (club_id, isbn, chapter, user_id, title, content))


def generate_sample_clubs(num_clubs=15):
    """Generate sample book clubs with members and discussions"""
    
    print(f"  Generating {num_clubs} sample book clubs...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Get random users and books
        print("  Fetching random users and books...")
        all_users = get_random_users(cursor, num_clubs * 20)
        all_books = get_random_books(cursor, num_clubs * 10)
        
        for i in range(num_clubs):
            club_name = f"Book Club {i + 1}"
            description = f"A wonderful book club for passionate readers!"
            is_public = random.choice([True, False])
            creator_id = all_users[i]
            
            # Create club
            club_id = create_club(cursor, club_name, description, is_public, creator_id)
            
            # Add creator as admin
            add_club_member(cursor, club_id, creator_id, 'admin')
            
            # Add random members (5-15 per club)
            num_members = random.randint(5, 15)
            member_ids = random.sample(all_users, num_members)
            
            moderator_count = 0
            for member_id in member_ids:
                if member_id == creator_id:
                    continue
                
                # Randomly assign moderators (max 3)
                role = 'member'
                if moderator_count < 3 and random.random() < 0.2:
                    role = 'moderator'
                    moderator_count += 1
                
                add_club_member(cursor, club_id, member_id, role)
            
            # Set current book
            current_book = random.choice(all_books)
            set_current_book(cursor, club_id, current_book)
            
            # Add books to reading queue
            queue_size = random.randint(2, 5)
            for pos in range(1, queue_size + 1):
                book = random.choice(all_books)
                add_to_queue(cursor, club_id, book, pos, creator_id)
            
            # Add reading history
            history_size = random.randint(1, 3)
            for _ in range(history_size):
                book = random.choice(all_books)
                add_to_history(cursor, club_id, book)
            
            # Create general discussions
            num_general = random.randint(1, 3)
            for j in range(num_general):
                user = random.choice(member_ids)
                title = f"General Discussion Topic {j + 1}"
                content = "This is an interesting topic for discussion!"
                create_general_discussion(cursor, club_id, user, title, content)
            
            # Create chapter discussions
            num_chapter = random.randint(2, 4)
            for j in range(num_chapter):
                user = random.choice(member_ids)
                chapter = random.randint(1, 10)
                title = f"Chapter {chapter} Discussion"
                content = f"What did everyone think about chapter {chapter}?"
                create_chapter_discussion(cursor, club_id, current_book, chapter, 
                                        user, title, content)
            
            conn.commit()
            print(f"    Created club {i + 1}/{num_clubs}: {club_name}")
        
        print(f"  [SUCCESS] Generated {num_clubs} sample clubs!")
        
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    generate_sample_clubs(30)