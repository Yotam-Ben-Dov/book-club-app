import pandas as pd
import mysql.connector
from config import DB_CONFIG, BOOKS_FILE, MIN_YEAR, MAX_YEAR, BATCH_SIZE


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def clean_field(value):
    """Clean and validate field"""
    if pd.isna(value):
        return None
    value = str(value).strip()
    return value if value else None


def is_valid_isbn(isbn):
    """Validate ISBN format"""
    if not isbn:
        return False
    isbn_clean = isbn.replace('-', '').replace(' ', '')
    return 10 <= len(isbn_clean) <= 13 and isbn_clean.isdigit()


def load_publishers(cursor, conn, publishers):
    """Load publishers and return name->id mapping"""
    publisher_map = {}
    
    sql = "INSERT IGNORE INTO Publishers(name) VALUES (%s)"
    
    batch = []
    count = 0
    
    for publisher in publishers:
        if not publisher:
            continue
        batch.append((publisher,))
        count += 1
        
        if len(batch) >= BATCH_SIZE:
            cursor.executemany(sql, batch)
            conn.commit()
            batch = []
            print(f"    Processing {count} publishers...")
    
    if batch:
        cursor.executemany(sql, batch)
        conn.commit()
    
    cursor.execute("SELECT publisher_id, name FROM Publishers")
    for pid, name in cursor.fetchall():
        publisher_map[name] = pid
    
    print(f"    Total unique publishers loaded: {len(publisher_map)}")
    return publisher_map


def load_authors(cursor, conn, authors):
    """Load authors and return name->id mapping"""
    author_map = {}
    
    sql = "INSERT IGNORE INTO Authors(name) VALUES (%s)"
    
    batch = []
    count = 0
    
    for author in authors:
        if not author:
            continue
        batch.append((author,))
        count += 1
        
        if len(batch) >= BATCH_SIZE:
            cursor.executemany(sql, batch)
            conn.commit()
            batch = []
            print(f"    Processing {count} authors...")
    
    if batch:
        cursor.executemany(sql, batch)
        conn.commit()
    
    cursor.execute("SELECT author_id, name FROM Authors")
    for aid, name in cursor.fetchall():
        author_map[name] = aid
    
    print(f"    Total unique authors loaded: {len(author_map)}")
    return author_map


def load_books(cursor, conn, df, publisher_map):
    """Load books - UPDATED for single image_url field"""
    # Use Image-URL-M (medium) as the single image_url
    sql = """INSERT IGNORE INTO Books(ISBN, title, year_of_publication, publisher_id, image_url) 
             VALUES (%s, %s, %s, %s, %s)"""
    
    batch = []
    count = 0
    skipped = 0
    
    for _, row in df.iterrows():
        try:
            isbn = row['ISBN']
            title = row['Book-Title']
            year = int(row['Year-Of-Publication']) if pd.notna(row['Year-Of-Publication']) else None
            publisher_id = publisher_map.get(row['Publisher'])
            # Use medium image URL as the single image_url
            img_url = row['Image-URL-M']
            
            batch.append((isbn, title, year, publisher_id, img_url))
            count += 1
            
            if len(batch) >= BATCH_SIZE:
                cursor.executemany(sql, batch)
                conn.commit()
                batch = []
                print(f"    Loaded {count} books...")
                
        except Exception as e:
            skipped += 1
    
    if batch:
        cursor.executemany(sql, batch)
        conn.commit()
    
    print(f"    Total books loaded: {count}")
    if skipped > 0:
        print(f"    Books skipped: {skipped}")


def load_book_authors(cursor, conn, df, author_map):
    """Load book-author relationships"""
    sql = "INSERT IGNORE INTO Book_Authors(ISBN, author_id) VALUES (%s, %s)"
    
    batch = []
    count = 0
    skipped = 0
    
    for _, row in df.iterrows():
        isbn = row['ISBN']
        author = row['Book-Author']
        author_id = author_map.get(author)
        
        if not author_id:
            skipped += 1
            continue
        
        try:
            batch.append((isbn, author_id))
            count += 1
            
            if len(batch) >= BATCH_SIZE:
                cursor.executemany(sql, batch)
                conn.commit()
                batch = []
                print(f"    Loaded {count} book-author links...")
                
        except Exception as e:
            skipped += 1
    
    if batch:
        cursor.executemany(sql, batch)
        conn.commit()
    
    print(f"    Total book-author links: {count}")
    if skipped > 0:
        print(f"    Links skipped: {skipped}")


def load_books_data():
    """Main function to load books data"""
    
    print("  Reading books.csv...")
    df = pd.read_csv(BOOKS_FILE, sep=';', encoding='ISO-8859-1', 
                     on_bad_lines='skip', low_memory=False)
    
    print(f"  Read {len(df)} rows from CSV")
    
    # Clean column names
    df.columns = df.columns.str.strip().str.replace('"', '')
    
    # Clean fields
    df['ISBN'] = df['ISBN'].apply(clean_field)
    df['Book-Title'] = df['Book-Title'].apply(clean_field)
    df['Book-Author'] = df['Book-Author'].apply(clean_field)
    df['Publisher'] = df['Publisher'].apply(clean_field)
    df['Image-URL-M'] = df['Image-URL-M'].apply(clean_field)
    
    # Convert year to numeric
    df['Year-Of-Publication'] = pd.to_numeric(df['Year-Of-Publication'], errors='coerce')
    
    print("  Filtering data...")
    # Filter books
    df = df[
        df['ISBN'].notna() &
        df['Book-Title'].notna() &           
        (df['Book-Title'].str.len() > 0) &
        df['Book-Author'].notna() &
        (df['Book-Author'].str.lower() != 'unknown') &
        df['ISBN'].apply(is_valid_isbn) &
        (
            df['Year-Of-Publication'].isna() |
            ((df['Year-Of-Publication'] >= MIN_YEAR) & 
             (df['Year-Of-Publication'] <= MAX_YEAR))
        )
    ]
    
    print(f"  Filtered to {len(df)} valid books")
        
    # Extract unique publishers and authors
    unique_publishers = df['Publisher'].dropna().unique()
    unique_authors = df['Book-Author'].dropna().unique()
    
    print(f"  Found {len(unique_publishers)} unique publishers")
    print(f"  Found {len(unique_authors)} unique authors")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        print("  Loading Publishers table...")
        publisher_map = load_publishers(cursor, conn, unique_publishers)
        
        print("  Loading Authors table...")
        author_map = load_authors(cursor, conn, unique_authors)
        
        print("  Loading Books table...")
        load_books(cursor, conn, df, publisher_map)
        
        print("  Loading Book_Authors table...")
        load_book_authors(cursor, conn, df, author_map)
        
        print("  [SUCCESS] Books data loaded successfully!")
        
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    load_books_data()