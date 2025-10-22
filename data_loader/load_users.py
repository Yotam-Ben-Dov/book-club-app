import pandas as pd
import mysql.connector
from datetime import datetime
from config import DB_CONFIG, USERS_FILE, MIN_AGE, MAX_AGE, BATCH_SIZE


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def clean_location(location):
    """Clean and format location string"""
    if pd.isna(location):
        return None
    
    location = str(location).strip().lower()
    
    # Filter out invalid locations
    if location in ['n/a', 'na', '', 'null']:
        return None
    
    # Split by comma
    parts = [part.strip() for part in location.split(',')]
    
    # Must have at least 2 parts (city, country)
    if len(parts) < 2:
        return None
    
    # Remove empty parts
    parts = [p for p in parts if p]
    
    if len(parts) < 2:
        return None
    
    return ', '.join(parts)


def calculate_birth_year(age):
    """Calculate birth year from age"""
    if pd.isna(age):
        return None
    
    try:
        age = int(age)
        if MIN_AGE <= age <= MAX_AGE:
            current_year = datetime.now().year
            return current_year - age
    except:
        pass
    
    return None


def load_users_data():
    """Main function to load users"""
    
    print("  Reading users.csv...")
    df = pd.read_csv(USERS_FILE, sep=';', encoding='ISO-8859-1', 
                     on_bad_lines='skip')
    
    print(f"  Read {len(df)} rows from CSV")
    
    # Clean column names
    df.columns = df.columns.str.strip().str.replace('"', '')
    
    # Clean and transform data
    df['User-ID'] = pd.to_numeric(df['User-ID'], errors='coerce')
    df['Location-Clean'] = df['Location'].apply(clean_location)
    df['Birth-Year'] = df['Age'].apply(calculate_birth_year)
    
    print("  Filtering data...")
    # Filter users
    df = df[
        df['User-ID'].notna() & 
        (df['User-ID'] > 0) &
        df['Location-Clean'].notna() & 
        df['Birth-Year'].notna()
    ]
    
    print(f"  Filtered to {len(df)} valid users")
        
    # Create usernames and passwords
    df['Username'] = 'user' + df['User-ID'].astype(int).astype(str)
    df['Password'] = 'password123'
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        print("  Loading Users table...")
        sql = """INSERT INTO Users(user_id, username, password, location, birth_year) 
                 VALUES (%s, %s, %s, %s, %s)"""
        
        batch = []
        count = 0
        skipped = 0
        
        for _, row in df.iterrows():
            try:
                user_id = int(row['User-ID'])
                username = row['Username']
                password = row['Password']
                location = row['Location-Clean']
                birth_year = int(row['Birth-Year']) if pd.notna(row['Birth-Year']) and pd.notnull(row['Birth-Year']) else None
                
                batch.append((user_id, username, password, location, birth_year))
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
        
        print(f"    Total users loaded: {count}")
        print(f"    Users skipped: {skipped}")
        print("  ✓ Users data loaded successfully!")
        
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    load_users_data()