# Book Club Management System

## Project Information

**Submited by**: Yotam Ben Dov
**Submited to**: Osnat Drien
**Dataset**: https://www.kaggle.com/datasets/saurabhbagchi/books-dataset/data

## Installation Instructions

### Database Setup

Create the database and tables:

```bash
mysql -u root -p < schema.sql
```

### Data Loading

Make sure config is in the data_loader folder, and run data_loader py with:
```bash
python data_loader.py
```

Afterwards return config.py to be in the same folder as main.py
### Run Application

```bash
python main.py
```

## Database Schema

### Core Tables

**Books**: ISBN (PK), title, year_of_publication, publisher_id (FK), image_url  
**Authors**: author_id (PK), name  
**Book_Authors**: ISBN (FK), author_id (FK) - Junction table for many-to-many relationship  
**Publishers**: publisher_id (PK), name  
**Users**: user_id (PK), username, password, location, birth_year  
**Ratings**: rating_id (PK), user_id (FK), ISBN (FK), rating

### Club Management Tables

**Book_Clubs**: club_id (PK), name, description, is_public, created_by (FK), max_members  
**Club_Members**: club_id (FK), user_id (FK), role  
**Reading_Queue**: queue_id (PK), club_id (FK), ISBN (FK), queue_position, added_by (FK)  
**Reading_History**: history_id (PK), club_id (FK), ISBN (FK), start_date, end_date  
**General_Discussions**: discussion_id (PK), club_id (FK), user_id (FK), title, content, created_date  
**Chapter_Discussions**: discussion_id (PK), club_id (FK), ISBN (FK), chapter_number, user_id (FK), title, content, created_date

## Application Features

### Books Tab

**CRUD Operations**:
- Create: Add books with multiple authors, publisher, year, and image URL
- Read: Search by title, author, ISBN, publisher, or year; view detailed information with rating distribution
- Update: Edit title, publisher, year, and image URL
- Delete: Remove books (cascades to ratings and club references)

### Users Tab

**CRUD Operations**:
- Create: Add users with auto-suggested ID, username, password, location, and birth year
- Read: Search by username, location, or birth year; view reading statistics
- Update: Edit username, password, location, and birth year
- Delete: Remove users (cascades to ratings and club memberships)

**Analytics**: User reading statistics showing books rated, average rating given, unique authors, and favorite author

### Ratings Tab

**CRUD Operations**:
- Create: Add ratings (0-10 scale) with validation for user and book existence
- Read: Filter by user ID, ISBN, or minimum rating
- Update: Modify existing ratings
- Delete: Remove ratings

### Clubs Tab

**Club Management**:
- Create clubs with name, description, public/private setting, and creator
- Edit club details
- Delete clubs (cascades to all related data)

**Members Sub-Tab**:
- Add members with roles (admin, moderator, member)
- Remove members
- Change member roles

**Reading Queue Sub-Tab**:
- Add books to club reading queue
- Remove books from queue
- Start reading (moves book to history)

**Reading History Sub-Tab**:
- View completed books and current book
- Complete current book (sets end_date)

**Discussions Sub-Tab**:
- Create general or chapter-specific discussions
- View discussion details with comments
- Add comments to discussions
- Delete discussions

### Analytics Tab

Contains two categories of queries.

## Complex Queries

### Query 1: Top Publishers by Rating

**Location**: `db/analytics_dao.py` - `get_top_publishers_by_rating()`

**Purpose**: Analyzes publishers by average rating and book count

**Parameters**: 
- min_books (default: 5)
- min_ratings (default: 50)

**Complexity Features**:
- Multiple JOINs (Publishers → Books → Ratings)
- GROUP BY with multiple columns
- Aggregations: COUNT(DISTINCT), AVG(), ROUND()
- HAVING clause with compound conditions
- ORDER BY with multiple criteria

**SQL**:
```sql
SELECT 
    p.name AS publisher_name,
    COUNT(DISTINCT b.ISBN) AS total_books,
    ROUND(AVG(r.rating), 2) AS avg_rating,
    COUNT(r.rating_id) AS total_ratings
FROM Publishers p
JOIN Books b ON p.publisher_id = b.publisher_id
JOIN Ratings r ON b.ISBN = r.ISBN
GROUP BY p.publisher_id, p.name
HAVING COUNT(DISTINCT b.ISBN) >= 5 
   AND COUNT(r.rating_id) >= 50
ORDER BY avg_rating DESC, total_ratings DESC
```

### Query 2: Top Rated Books by Age Group

**Location**: `db/analytics_dao.py` - `get_top_rated_books_by_age_group()`

**Purpose**: Shows reading preferences across generations (Gen Z, Millennials, Gen X, Boomers+)

**Parameters**: 
- min_ratings (default: 10)

**Complexity Features**:
- CASE statements for age group classification
- Multiple JOINs (Users → Ratings → Books)
- GROUP BY on computed column (age_group)
- Aggregations: COUNT(), AVG(), ROUND()
- HAVING clause

**SQL**:
```sql
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
GROUP BY age_group, b.ISBN, b.title
HAVING num_ratings >= 10
ORDER BY age_group, avg_rating DESC, num_ratings DESC
```

### Query 3: Most Active Book Clubs

**Location**: `db/analytics_dao.py` - `get_most_active_book_clubs()`

**Purpose**: Analyzes club engagement with multiple metrics

**Parameters**: 
- min_members (default: 3)

**Complexity Features**:
- Multiple JOINs (5 tables: Book_Clubs → Club_Members → Reading_History → General_Discussions → Comments)
- Multiple COUNT(DISTINCT) aggregations
- Complex calculation (discussions_per_member with NULLIF to avoid division by zero)
- HAVING clause
- ORDER BY on calculated field

**SQL**:
```sql
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
HAVING member_count >= 3
ORDER BY discussions_per_member DESC, total_discussions DESC
```

## Simple Queries

All simple queries are accessible through the Analytics tab.

1. **Books Trending in Clubs** (`simple_queries_dao.py`): Books most frequently in reading queues
2. **Most Discussed Books** (`simple_queries_dao.py`): Books with most chapter discussions
3. **Publisher Comparison** (`simple_queries_dao.py`): Publishers ranked by metrics
4. **Most Prolific Authors** (`simple_queries_dao.py`): Authors by book count and ratings
5. **Location-Based Statistics** (`simple_queries_dao.py`): User distribution and popular books by region
6. **Top Rated Books** (`simple_queries_dao.py`): Highest rated books with threshold
7. **Club Activity Metrics** (`simple_queries_dao.py`): Activity statistics for all clubs
8. **User Reading Statistics** (`users_dao.py`): Individual user metrics
9. **Club Reading Queue** (`clubs_dao.py`): Books in club queue with details
10. **Club Reading History** (`clubs_dao.py`): Completed and current books

## Code Architecture

### Package Structure

```
book-club-app/
├── main.py                 # Application entry point
├── config.py               # Database configuration
├── schema.sql              # Database schema
├── db/                     # Database access layer
│   ├── connection.py       # Singleton connection manager
│   ├── books_dao.py        # Books CRUD operations
│   ├── users_dao.py        # Users CRUD operations
│   ├── ratings_dao.py      # Ratings CRUD operations
│   ├── clubs_dao.py        # Clubs CRUD operations
│   ├── authors_dao.py      # Authors operations
│   ├── publishers_dao.py   # Publishers operations
│   ├── analytics_dao.py    # Complex analytical queries
│   └── simple_queries_dao.py # Simple analytical queries
├── core/
│   └── validators.py       # Input validation functions
├── ui/                     # User interface layer
│   ├── main_window.py      # Main application window
│   ├── books_tab.py        # Books management tab
│   ├── users_tab.py        # Users management tab
│   ├── ratings_tab.py      # Ratings management tab
│   ├── clubs_tab.py        # Clubs management tab
│   ├── analytics_tab.py    # Analytics queries tab
│   └── dialogs.py          # Modal dialogs for CRUD operations
└── data_loader/            # Data import scripts
    ├── load_books.py
    ├── load_users.py
    ├── load_ratings.py
    └── generate_sample_clubs.py
```
