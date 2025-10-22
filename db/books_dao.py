"""
Books data access object
Handles book-related database operations
"""

from db.connection import db
from db.authors_dao import get_or_create_author
from db.publishers_dao import get_or_create_publisher


def search_books(title=None, author=None, isbn=None, publisher=None, year=None, limit=100):
    """
    Search books with multiple filters
    
    Returns list of books with author and publisher info
    """
    query = """
        SELECT 
            b.ISBN,
            b.title,
            b.year_of_publication,
            b.image_url,
            p.name as publisher_name,
            p.publisher_id,
            GROUP_CONCAT(DISTINCT a.name SEPARATOR ', ') as authors,
            ROUND(AVG(r.rating), 2) as avg_rating,
            COUNT(r.rating_id) as rating_count
        FROM Books b
        LEFT JOIN Publishers p ON b.publisher_id = p.publisher_id
        LEFT JOIN Book_Authors ba ON b.ISBN = ba.ISBN
        LEFT JOIN Authors a ON ba.author_id = a.author_id
        LEFT JOIN Ratings r ON b.ISBN = r.ISBN
        WHERE 1=1
    """
    
    params = []
    
    if title:
        query += " AND b.title LIKE %s"
        params.append(f"%{title}%")
    
    if author:
        query += " AND a.name LIKE %s"
        params.append(f"%{author}%")
    
    if isbn:
        query += " AND b.ISBN LIKE %s"
        params.append(f"%{isbn}%")
    
    if publisher:
        query += " AND p.name LIKE %s"
        params.append(f"%{publisher}%")
    
    if year:
        query += " AND b.year_of_publication = %s"
        params.append(year)
    
    query += " GROUP BY b.ISBN, b.title, b.year_of_publication, b.image_url, p.name, p.publisher_id"
    query += " ORDER BY b.title"
    query += f" LIMIT {limit}"
    
    return db.execute_query(query, tuple(params))

def get_book_by_isbn(isbn):
    """Get detailed book information by ISBN"""
    query = """
        SELECT 
            b.ISBN,
            b.title,
            b.year_of_publication,
            b.image_url,
            p.name as publisher_name,
            p.publisher_id,
            GROUP_CONCAT(DISTINCT a.name SEPARATOR ', ') as authors,
            GROUP_CONCAT(DISTINCT a.author_id SEPARATOR ',') as author_ids,
            AVG(r.rating) as avg_rating,
            COUNT(DISTINCT r.rating_id) as rating_count
        FROM Books b
        LEFT JOIN Publishers p ON b.publisher_id = p.publisher_id
        LEFT JOIN Book_Authors ba ON b.ISBN = ba.ISBN
        LEFT JOIN Authors a ON ba.author_id = a.author_id
        LEFT JOIN Ratings r ON b.ISBN = r.ISBN
        WHERE b.ISBN = %s
        GROUP BY b.ISBN, b.title, b.year_of_publication, b.image_url, p.name, p.publisher_id
    """
    return db.execute_query(query, (isbn,), fetch_one=True)


def add_book(isbn, title, author_names, publisher_name=None, year=None, image_url=None):
    """
    Add a new book with authors and publisher
    
    Args:
        isbn: Book ISBN
        title: Book title
        author_names: List of author names or single author name
        publisher_name: Publisher name (optional)
        year: Year of publication (optional)
        image_url: Book cover URL (optional)
    
    Returns:
        True on success, False on error
    """
    # Ensure author_names is a list
    if isinstance(author_names, str):
        author_names = [author_names]
    
    # Get or create publisher
    publisher_id = None
    if publisher_name:
        publisher_id = get_or_create_publisher(publisher_name)
    
    # Get or create authors
    author_ids = []
    for author_name in author_names:
        if author_name:
            author_id = get_or_create_author(author_name.strip())
            if author_id:
                author_ids.append(author_id)
    
    if not author_ids:
        print("Error: No valid authors provided")
        return False
    
    # Prepare operations for transaction
    operations = []
    
    # Insert book
    book_query = """
        INSERT INTO Books(ISBN, title, year_of_publication, publisher_id, image_url)
        VALUES (%s, %s, %s, %s, %s)
    """
    operations.append((book_query, (isbn, title, year, publisher_id, image_url)))
    
    # Insert book-author relationships
    for author_id in author_ids:
        ba_query = "INSERT INTO Book_Authors(ISBN, author_id) VALUES (%s, %s)"
        operations.append((ba_query, (isbn, author_id)))
    
    # Execute transaction
    return db.execute_transaction(operations)


def update_book(isbn, title=None, year=None, publisher_name=None, image_url=None):
    """
    Update book information (not authors - use separate functions)
    """
    # Build dynamic update query
    updates = []
    params = []
    
    if title is not None:
        updates.append("title = %s")
        params.append(title)
    
    if year is not None:
        updates.append("year_of_publication = %s")
        params.append(year)
    
    if publisher_name is not None:
        publisher_id = get_or_create_publisher(publisher_name) if publisher_name else None
        updates.append("publisher_id = %s")
        params.append(publisher_id)
    
    if image_url is not None:
        updates.append("image_url = %s")
        params.append(image_url)
    
    if not updates:
        return False
    
    params.append(isbn)
    query = f"UPDATE Books SET {', '.join(updates)} WHERE ISBN = %s"
    
    rows = db.execute_update(query, tuple(params))
    return rows is not None and rows > 0


def delete_book(isbn):
    """Delete book (cascades to Book_Authors and Ratings)"""
    query = "DELETE FROM Books WHERE ISBN = %s"
    rows = db.execute_update(query, (isbn,))
    return rows is not None and rows > 0


def get_book_authors(isbn):
    """Get all authors for a book"""
    query = """
        SELECT a.author_id, a.name
        FROM Authors a
        JOIN Book_Authors ba ON a.author_id = ba.author_id
        WHERE ba.ISBN = %s
        ORDER BY a.name
    """
    return db.execute_query(query, (isbn,))


def add_book_author(isbn, author_name):
    """Add an author to a book"""
    author_id = get_or_create_author(author_name)
    query = "INSERT IGNORE INTO Book_Authors(ISBN, author_id) VALUES (%s, %s)"
    rows = db.execute_update(query, (isbn, author_id))
    return rows is not None


def remove_book_author(isbn, author_id):
    """Remove an author from a book"""
    query = "DELETE FROM Book_Authors WHERE ISBN = %s AND author_id = %s"
    rows = db.execute_update(query, (isbn, author_id))
    return rows is not None and rows > 0


def get_books_by_publisher(publisher_id, limit=100):
    """Get all books by a publisher (Simple Query #8)"""
    query = """
        SELECT 
            b.ISBN,
            b.title,
            b.year_of_publication,
            GROUP_CONCAT(a.name SEPARATOR ', ') as authors,
            AVG(r.rating) as avg_rating
        FROM Books b
        LEFT JOIN Book_Authors ba ON b.ISBN = ba.ISBN
        LEFT JOIN Authors a ON ba.author_id = a.author_id
        LEFT JOIN Ratings r ON b.ISBN = r.ISBN
        WHERE b.publisher_id = %s
        GROUP BY b.ISBN, b.title, b.year_of_publication
        ORDER BY b.title
        LIMIT %s
    """
    return db.execute_query(query, (publisher_id, limit))