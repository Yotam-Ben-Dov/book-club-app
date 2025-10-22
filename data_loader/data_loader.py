#!/usr/bin/env python3
"""
Main data loader script for Book Club Database
Orchestrates loading of all data from CSV files
"""

import mysql.connector
import time
from config import DB_CONFIG
from load_books import load_books_data
from load_users import load_users_data
from load_ratings import load_ratings_data
from generate_sample_clubs import generate_sample_clubs


def get_connection():
    """Create database connection"""
    return mysql.connector.connect(**DB_CONFIG)


def main():
    """Main data loading orchestrator"""
    print("=" * 60)
    print("BOOK CLUB DATABASE - DATA LOADER")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        # Test connection
        print("\n[0/4] Testing database connection...")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE()")
        db_name = cursor.fetchone()[0]
        print(f"[SUCCESS] Connected to database: {db_name}")
        cursor.close()
        conn.close()
        
        # Load books (includes publishers and authors)
        print("\n[1/4] Loading Books, Authors, and Publishers...")
        load_books_data()
        
        # Load users
        print("\n[2/4] Loading Users...")
        load_users_data()
        
        # Load ratings
        print("\n[3/4] Loading Ratings...")
        load_ratings_data()
        
        # Generate sample clubs (optional)
        print("\n[4/4] Generating Sample Book Clubs...")
        response = input("Generate sample book clubs? (y/n): ").strip().lower()
        if response == 'y':
            num_clubs = int(input("How many clubs? (10-20 recommended): "))
            generate_sample_clubs(num_clubs)
        else:
            print("Skipping sample club generation.")
        
        elapsed_time = time.time() - start_time
        print("\n" + "=" * 60)
        print(f"[SUCCESS] DATA LOADING COMPLETE!")
        print(f"Total time: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())