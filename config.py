DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'database': 'book_club_db',
    'user': 'root',
    'password': 'Fuckyounopassword1!',  # CHANGE THIS
    'charset': 'utf8mb4',
    'use_unicode': True
}

# Data file paths
DATA_DIR = './data/'
BOOKS_FILE = DATA_DIR + 'books.csv'
USERS_FILE = DATA_DIR + 'users.csv'
RATINGS_FILE = DATA_DIR + 'ratings.csv'

# Filtering criteria
MIN_YEAR = 1900
MAX_YEAR = 2025
MIN_AGE = 6
MAX_AGE = 120
MIN_USER_RATINGS = 3
BATCH_SIZE = 1000