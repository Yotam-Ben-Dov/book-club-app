-- ============================================
-- Submitted by: Yotam Ben Dov
-- Submitted to: Osnat Drien
-- ============================================
DROP DATABASE IF EXISTS db11;

CREATE DATABASE db11
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE db11;

CREATE TABLE Publishers (
    publisher_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    INDEX idx_name (name)
) ENGINE=InnoDB;

CREATE TABLE Authors (
    author_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    INDEX idx_name (name)
) ENGINE=InnoDB;

CREATE TABLE Books (
    ISBN VARCHAR(13) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    year_of_publication YEAR,
    publisher_id INT,
    image_url VARCHAR(255),
    INDEX idx_title (title),
    INDEX idx_year (year_of_publication),
    FOREIGN KEY (publisher_id) REFERENCES Publishers(publisher_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Book_Authors (
    ISBN VARCHAR(13),
    author_id INT,
    PRIMARY KEY (ISBN, author_id),
    FOREIGN KEY (ISBN) REFERENCES Books(ISBN)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (author_id) REFERENCES Authors(author_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Users (
    user_id INT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL, 
    birth_year YEAR NOT NULL,
    INDEX idx_username (username),
    INDEX idx_location (location),
    INDEX idx_birth_year (birth_year)
) ENGINE=InnoDB;

CREATE TABLE Ratings (
    rating_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    ISBN VARCHAR(13) NOT NULL,
    rating TINYINT NOT NULL CHECK (rating >= 0 AND rating <= 10),
    UNIQUE KEY unique_user_book (user_id, ISBN),
    INDEX idx_user (user_id),
    INDEX idx_book (ISBN),
    INDEX idx_rating (rating),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (ISBN) REFERENCES Books(ISBN)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Book_Clubs (
    club_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT TRUE,
    created_by INT NOT NULL,
    max_members INT DEFAULT 50,
    INDEX idx_name (name),
    INDEX idx_public (is_public),
    INDEX idx_creator (created_by),
    FOREIGN KEY (created_by) REFERENCES Users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Club_Members (
    club_id INT,
    user_id INT,
    role ENUM('admin', 'moderator', 'member') DEFAULT 'member',
    PRIMARY KEY (club_id, user_id),
    INDEX idx_club_role (club_id, role),
    FOREIGN KEY (club_id) REFERENCES Book_Clubs(club_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Reading_Queue (
    queue_id INT AUTO_INCREMENT PRIMARY KEY,
    club_id INT NOT NULL,
    ISBN VARCHAR(13) NOT NULL,
    queue_position INT NOT NULL,
    added_by INT,
    UNIQUE KEY unique_club_book (club_id, ISBN),
    INDEX idx_club_position (club_id, queue_position),
    FOREIGN KEY (club_id) REFERENCES Book_Clubs(club_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (ISBN) REFERENCES Books(ISBN)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (added_by) REFERENCES Users(user_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Reading_History (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    club_id INT NOT NULL,
    ISBN VARCHAR(13) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NULL,
    UNIQUE KEY unique_club_current_book (club_id, ISBN, start_date),
    INDEX idx_club (club_id),
    INDEX idx_dates (start_date, end_date),
    INDEX idx_current_book (club_id, end_date), 
    FOREIGN KEY (club_id) REFERENCES Book_Clubs(club_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (ISBN) REFERENCES Books(ISBN)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT chk_dates CHECK (end_date IS NULL OR end_date >= start_date)
) ENGINE=InnoDB;

CREATE TABLE General_Discussions (
    discussion_id INT AUTO_INCREMENT PRIMARY KEY,
    club_id INT NOT NULL,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_club_date (club_id, created_date DESC),
    FOREIGN KEY (club_id) REFERENCES Book_Clubs(club_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Chapter_Discussions (
    discussion_id INT AUTO_INCREMENT PRIMARY KEY,
    club_id INT NOT NULL,
    ISBN VARCHAR(13) NOT NULL,
    chapter_number INT NOT NULL,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_club_book_chapter (club_id, ISBN, chapter_number),
    INDEX idx_club_date (club_id, created_date DESC),
    FOREIGN KEY (club_id) REFERENCES Book_Clubs(club_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (ISBN) REFERENCES Books(ISBN)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE General_Discussion_Comments (
    comment_id INT AUTO_INCREMENT PRIMARY KEY,
    discussion_id INT NOT NULL,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_discussion_date (discussion_id, created_date),
    FOREIGN KEY (discussion_id) REFERENCES General_Discussions(discussion_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Chapter_Discussion_Comments (
    comment_id INT AUTO_INCREMENT PRIMARY KEY,
    discussion_id INT NOT NULL,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_discussion_date (discussion_id, created_date),
    FOREIGN KEY (discussion_id) REFERENCES Chapter_Discussions(discussion_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

SELECT 'works' AS Status;
SHOW TABLES;