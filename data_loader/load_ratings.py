"""
Load ratings from ratings.csv with filtering
"""

import pandas as pd
import mysql.connector
from config import DB_CONFIG, RATINGS_FILE, BATCH_SIZE


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def get_valid_users(cursor):
    """Get set of valid user IDs from database"""
    cursor.execute("SELECT user_id FROM Users")
    return set(row[0] for row in cursor.fetchall())


def get_valid_books(cursor):
    """Get set of valid ISBNs from database"""
    cursor.execute("SELECT ISBN FROM Books")
    return set(row[0] for row in cursor.fetchall())


def load_ratings_data():
    """Main function to load ratings"""
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Get valid users and books
        print("  Loading valid user IDs...")
        valid_users = get_valid_users(cursor)
        print(f"    Found {len(valid_users)} valid users")
        
        print("  Loading valid ISBNs...")
        valid_books = get_valid_books(cursor)
        print(f"    Found {len(valid_books)} valid books")
        
        print("  Reading ratings.csv...")
        # Read in chunks to handle large file
        chunk_size = 50000
        chunks = pd.read_csv(RATINGS_FILE, sep=';', encoding='ISO-8859-1',
                            on_bad_lines='skip', chunksize=chunk_size)
        
        sql = "INSERT INTO Ratings(user_id, ISBN, rating) VALUES (%s, %s, %s)"
        
        total_count = 0
        total_skipped = 0
        chunk_num = 0
        
        for chunk in chunks:
            chunk_num += 1
            print(f"  Processing chunk {chunk_num}...")
            
            # Clean column names
            chunk.columns = chunk.columns.str.strip().str.replace('"', '')
            
            # Clean data
            chunk['User-ID'] = pd.to_numeric(chunk['User-ID'], errors='coerce')
            chunk['Book-Rating'] = pd.to_numeric(chunk['Book-Rating'], errors='coerce')
            chunk['ISBN'] = chunk['ISBN'].astype(str).str.strip()
            
            # Filter ratings
            chunk = chunk[
                chunk['User-ID'].notna() &
                chunk['ISBN'].notna() &
                chunk['Book-Rating'].notna() &
                (chunk['Book-Rating'] > 0) &  # Exclude 0 ratings
                chunk['User-ID'].isin(valid_users) &
                chunk['ISBN'].isin(valid_books)
            ]
            
            # Load batch
            batch = []
            count = 0
            skipped = 0
            
            for _, row in chunk.iterrows():
                try:
                    user_id = int(row['User-ID'])
                    isbn = row['ISBN']
                    rating = int(row['Book-Rating'])
                    
                    batch.append((user_id, isbn, rating))
                    count += 1
                    
                    if len(batch) >= BATCH_SIZE:
                        cursor.executemany(sql, batch)
                        conn.commit()
                        batch = []
                        
                except Exception as e:
                    skipped += 1
            
            if batch:
                cursor.executemany(sql, batch)
                conn.commit()
            
            total_count += count
            total_skipped += skipped
            print(f"    Chunk {chunk_num}: loaded {count} ratings, skipped {skipped}")
        
        print(f"  Total ratings loaded: {total_count}")
        print(f"  Total ratings skipped: {total_skipped}")
        print("  [SUCCESS] Ratings data loaded successfully!")
        
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    load_ratings_data()